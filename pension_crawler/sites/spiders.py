'''spiders.py'''

from datetime import datetime
from urllib.parse import urlparse, urlunparse

from scrapy import Request

from pension_crawler.items import PDFLoader
from pension_crawler.utils import BaseSpider

from .settings import SETTINGS


class SitesSpider(BaseSpider):

    '''Extract pdf files from a list of sites.'''

    # class variables

    name = 'sites'
    custom_settings = SETTINGS

    # constructor

    def __init__(self, crawler, data, *args, **kwargs):
        '''Set crawler and input list.'''
        super(SitesSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.data = data
        self.years = [str(year) for year in range(1960,2019,1)]

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass crawler and start urls to constructor.'''
        data = SitesSpider._data(crawler.settings)
        return cls(crawler, data, *args, **kwargs)

    # private methods

    def _href(self, url, node):
        '''Get href full location.'''
        parsed_url = urlparse(url)
        href = node.xpath('@href').extract_first().replace('../', '')
        parsed_href = urlparse(href)
        if not (parsed_href.scheme or parsed_href.netloc):
            parsed_href = parsed_href._replace(scheme=parsed_url.scheme)
            parsed_href = parsed_href._replace(netloc=parsed_url.netloc)
        return urlunparse(parsed_href)

    def _process_item(self, url, node):
        '''Load PDF item.'''
        href = self._href(url, node)
        loader = PDFLoader(selector=node)
        loader.add_value('url', url)
        loader.add_value('href', href)
        loader.add_xpath('text', 'text()')
        loader.add_value('file_urls', [href])
        loader.add_value('timestamp', datetime.now().isoformat())
        
        '''
        Code added by Joseph J. Bautista
        - Context: Some links were missing in the output.csv file while it was clear that the year
        was present in the link. This is the proposed solution for that.
        '''
        href = href.split('/')[-1].split('.')[0]
        i = 0
        year_stack = []
        for year in self.years:
            if year in link:
                i = i + 1
                year_stack.append(year)
            elif "FY{}".format(year[-2:]) in link:
                i = i + 1
                year_stack.append(year)
            elif "FY-{}".format(year[-2:]) in link:
                i = i + 1
                year_stack.append(year)
            elif "fy{}".format(year[-2:]) in link:
                i = i + 1
            elif "fy-{}".format(year[-2:]) in link:
                i = i + 1
        if == 1:
            loader.add_value('year', year)
        elif i > 1:
            loader.add_value('year', year_stack[-1])
        
        return loader.load_item()

    # class method overrides

    def start_requests(self):
        '''Dispatch requests per site url.'''
        for row in self.data:
            yield Request(row.get('url'), meta=self._meta(row))

    def parse(self, response):
        '''Parse search results.'''
        pdf_nodes = response.xpath('//a[contains(@href,".pdf")]')
        if len(pdf_nodes) > 1:
            for node in pdf_nodes:
                item = self._process_item(response.url, node)
                item = self._process_meta(item, response.meta)
                yield item
        else:
            '''
            Code added by Joseph J. Bautista
            - Context: Some sites have reports that don't link directly to the report. This serves as a flag.
            - NOTE: Needs some improvement as you'd have to filter out sites that actually work later on. Just a prototype.
            - SAMPLE COMMAND: scrapy crawl sites -o WeirdSites.json
            '''
            url = response.url
            yield {
                'url': url
            }
