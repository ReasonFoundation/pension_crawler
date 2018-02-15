'''spiders.py'''

import json
import logging

from datetime import datetime
from urllib.parse import urlparse, urlunparse

from scrapy import Spider
from scrapy.exceptions import NotConfigured

from pension_crawler.items import PDFLoader

from .settings import SETTINGS


logger = logging.getLogger(__name__)


class SitesSpider(Spider):

    '''Extract pdf files from a list of sites.'''

    name = 'sites'
    custom_settings = SETTINGS

    def __init__(self, crawler, start_urls, *args, **kwargs):
        '''Set crawler and url list.'''
        super(SitesSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.start_urls = start_urls

    @staticmethod
    def get_list_from_file(settings):
        '''Return values from file input.'''
        input_file = settings.get('INPUT_FILE')
        with open(input_file, 'r') as file_:
            return [i.strip() for i in file_.readlines()]

    @staticmethod
    def get_list_from_args(args):
        '''Return values from spider arguments.'''
        start_urls = args.pop('start_urls', None)
        if not start_urls:
            return
        try:
            return json.loads(start_urls)
        except ValueError:
            raise NotConfigured('Start url list from args is invalid.')

    @staticmethod
    def get_start_urls(args, settings):
        start_urls = SitesSpider.get_list_from_args(args)
        if not start_urls:
            logger.info('Start url list from args is empty.')
            start_urls = SitesSpider.get_list_from_file(settings)
        if not start_urls:
            raise NotConfigured('Start url list from file is empty.')
        return start_urls

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass crawler and start urls to constructor.'''
        start_urls = SitesSpider.get_start_urls(kwargs, crawler.settings)
        return cls(crawler, start_urls,  *args, **kwargs)

    def get_href(self, url, node):
        '''Get href full location.'''
        parsed_url = urlparse(url)
        href = node.xpath('@href').extract_first()
        parsed_href = urlparse(href)
        if not (parsed_href.scheme or parsed_href.netloc):
            parsed_href.scheme = parsed_url.scheme
            parsed_href.netloc = parsed_url.netloc
        return urlparse(parsed_href)

    def process_item(self, url, node):
        '''Load PDF item.'''
        href = self.get_href(url, node)
        loader = PDFLoader()
        loader.add_value('url', url)
        loader.add_value('href', href)
        loader.add_xpath('text', 'text()')
        loader.add_value('file_urls', [href])
        loader.add_value('timestamp', datetime.now().isoformat())
        return loader.load_item()

    def parse(self, response):
        '''Parse search results.'''
        for node in response.xpath('//a[contains(@href,".pdf")]'):
            yield self.process_item(response.url, node)
