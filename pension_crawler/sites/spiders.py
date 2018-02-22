'''spiders.py'''

import json
import logging

from datetime import datetime
from urllib.parse import urlparse, urlunparse

from scrapy import Spider, Request

from pension_crawler.items import PDFLoader
from pension_crawler.utils import SitesParser

from .settings import SETTINGS


logger = logging.getLogger(__name__)


class SitesSpider(Spider):

    '''Extract pdf files from a list of sites.'''

    # class variables

    name = 'sites'
    custom_settings = SETTINGS

    # constructor

    def __init__(self, crawler, input_list, *args, **kwargs):
        '''Set crawler and input list.'''
        super(SitesSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.input_list = input_list

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass crawler and start urls to constructor.'''
        parser = SitesParser(kwargs, crawler.settings)
        return cls(crawler, parser.input_list,  *args, **kwargs)

    # private methods

    def _get_href(self, url, node):
        '''Get href full location.'''
        parsed_url = urlparse(url)
        href = node.xpath('@href').extract_first()
        parsed_href = urlparse(href)
        if not (parsed_href.scheme or parsed_href.netloc):
            parsed_href = parsed_href._replace(scheme=parsed_url.scheme)
            parsed_href = parsed_href._replace(netloc=parsed_url.netloc)
        return urlunparse(parsed_href)

    def _load_item(self, url, node):
        '''Load PDF item.'''
        href = self._get_href(url, node)
        loader = PDFLoader(selector=node)
        loader.add_value('url', url)
        loader.add_value('href', href)
        loader.add_xpath('text', 'text()')
        loader.add_value('file_urls', [href])
        loader.add_value('timestamp', datetime.now().isoformat())
        return loader.load_item()

    # class method overrides

    def start_requests(self):
        '''Dispatch requests per site url.'''
        for url in self.input_list:
            yield Request(url)

    def parse(self, response):
        '''Parse search results.'''
        for node in response.xpath('//a[contains(@href,".pdf")]'):
            yield self._load_item(response.url, node)
