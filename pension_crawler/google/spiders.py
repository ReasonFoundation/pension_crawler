'''spiders.py'''

import json

from datetime import datetime
from urllib.parse import urlencode

from scrapy import Request
from scrapy.exceptions import NotConfigured

from pension_crawler.loaders import ResultLoader
from pension_crawler.utils import SearchSpider

from .settings import SETTINGS


class GoogleSpider(SearchSpider):

    '''Parse Google Search API results.'''

    # class variables

    name = 'google'
    custom_settings = SETTINGS

    # constructor

    def __init__(self, crawler, data, depth, api_key, engine_id, *args,
                 **kwargs):
        '''Set data, depth, and api key.'''
        super(GoogleSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.data = data
        self.depth = depth
        self.api_key = api_key
        self.engine_id = engine_id

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        data = GoogleSpider._data(crawler.settings)
        depth = crawler.settings.get('DEPTH')
        api_key = crawler.settings.get('API_KEY')
        engine_id = crawler.settings.get('ENGINE_ID')
        if not depth:
            raise NotConfigured('Crawl depth not specified.')
        if not api_key:
            raise NotConfigured('API key not specified.')
        if not engine_id:
            raise NotConfigured('Engine ID not specified.')
        return cls(crawler, data, depth, api_key, engine_id, *args, **kwargs)

    # private methods

    def _date(self, text):
        try:
            datetime.strptime(text, '%Y%m%d')
            return text
        except ValueError:
            raise NotConfigured('Invalid date: {}'.format(text))

    def _url(self, row):
        '''Return request url.'''
        query = self._query(row)
        self.logger.info('Google spider - Request for query: {}'.format(query))
        data = {'cx': self.engine_id, 'key': self.api_key, 'q': query}
        start_date = row.get('start_date')
        end_date = row.get('end_date')
        if start_date and end_date:
            data['sort'] = 'date:r:{}:{}'.format(
                self._date(start_date), self._date(end_date)
            )
        base = 'https://www.googleapis.com/customsearch/v1?{}'
        return base.format(urlencode(data))

    def _process_item(self, node):
        '''Load single result item.'''
        loader = ResultLoader()
        loader.add_value('url', node['link'])
        loader.add_value('title', node['title'])
        loader.add_value('snippet', node['snippet'])
        loader.add_value('timestamp', datetime.now().isoformat())
        return loader.load_item()

    # class method overrides

    def start_requests(self):
        '''Dispatch requests per keyword.'''
        for row in self.data:
            yield Request(self._url(row), meta=self._meta(row))

    def parse(self, response):
        '''Parse search results.'''
        data = json.loads(response.body_as_unicode())
        results = data.get('items', [])
        message = 'Google spider - Found {} results for url: {}'
        self.logger.info(message.format(len(results), response.url))
        for node in results:
            item = self._process_item(node)
            item = self._process_meta(item, response.meta)
            item['keyword'] = data['queries']['request'][0]['searchTerms']
            item['total'] = data['searchInformation']['totalResults']
            item['file_urls'] = [item['url']]
            yield item

        # go to next results page

        if self.depth - 1:
            start = data['queries']['nextPage'][0]['startIndex']
            url = '{}&start={}'.format(response.request.url, start)
            yield Request(url, meta=response.meta)
            self.depth -= 1
            self.logger.info('Google spider - Processing next page.')
        else:
            self.logger.info('Google spider - Next page limit reached.')
