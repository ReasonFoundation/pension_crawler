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
        self.years = [str(year) for year in range(1960,2018,1)]

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass crawler and start urls to constructor.'''
        data = SitesSpider._data(crawler.settings)
        return cls(crawler, data, *args, **kwargs)

    # private methods
	"""
	The previous href variable assignment here was causing errors. The new one fixes that.
	-- Joseph J. Bautista
	"""
    def _href(self, url, node):
        '''Get href full location.'''
        parsed_url = urlparse(url)
        # href = node.xpath('@href').extract_first().replace('../', '')
        href = node.extract().replace("../", "")
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
        return loader.load_item()

    # class method overrides

    def start_requests(self):
        '''Dispatch requests per site url.'''
        for row in self.data:
            yield Request(row.get('url'), meta=self._meta(row))

	"""
	Changed the xpath command here to look for hrefs and only process those with the substring 'pdf' in them.
	-- Joseph J. Bautista
	"""
    def parse(self, response):
        '''Parse search results.'''
        # pdf_nodes = response.xpath('//a[contains(@href,".pdf")]')
        pdf_nodes = response.xpath("//@href")
        for node in pdf_nodes:
            href = node.extract()
            if "pdf" in href.lower():
                item = self._process_item(response.url, node)
                item = self._process_meta(item, response.meta)
                yield item
