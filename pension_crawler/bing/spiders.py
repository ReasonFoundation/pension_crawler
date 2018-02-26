'''spiders.py'''

import json
import os

from datetime import datetime
from urllib.parse import urlencode

from scrapy import Request
from scrapy.exceptions import NotConfigured

from pension_crawler.items import ResultLoader
from pension_crawler.utils import SearchSpider

from .settings import SETTINGS


class BingSpider(SearchSpider):

    '''Parse Bing Search API results.'''

    # class variables

    name = 'bing'
    custom_settings = SETTINGS

    # constructor

    def __init__(self, crawler, data, depth, api_key, *args, **kwargs):
        '''Set data, depth, and api key.'''
        super(BingSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.data = data
        self.depth = depth
        self.api_key = api_key

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        data = BingSpider._data(crawler.settings)
        depth = crawler.settings.get('depth')
        api_key = crawler.settings.get('api_key')
        if not depth:
            raise NotConfigured('Crawl depth not specified.')
        if not api_key:
            raise NotConfigured('API key not specified.')
        return cls(crawler, data, depth, api_key, *args, **kwargs)

    # properties

    @property
    def headers(self):
        '''Return request headers.'''
        return {'Ocp-Apim-Subscription-Key' : self.api_key}

    # private methods

    def _freshness(self, text):
        '''Check if freshness in allowed values.'''
        if not text in ['Day', 'Week', 'Month']:
            raise NotConfigured('Invalid freshness: {}'.format(text))
        return text

    def _url(self, row):
        '''Return request url.'''
        data = {'q': self._query(row)}
        freshness = row.get('freshness')
        if freshness:
            data['freshness'] = self._freshness(freshness)
        base = 'https://api.cognitive.microsoft.com/bing/v7.0/search?{}'
        return base.format(urlencode(data))

    def _process_item(self, node):
        '''Load single result item.'''
        loader = ResultLoader()
        loader.add_value('url', node['url'])
        loader.add_value('title', node['name'])
        loader.add_value('snippet', node['snippet'])
        loader.add_value('timestamp', datetime.now().isoformat())
        return loader.load_item()

    # overriden class methods

    def start_requests(self):
        '''Dispatch requests per keyword.'''
        for row in self.data:
            yield Request(
                self._url(row), meta=self._meta(row), headers=self.headers
            )

    def parse(self, response):
        '''Parse search results.'''
        data = json.loads(response.body_as_unicode())
        for node in data.get('webPages', {}).get('value', []):
            item = self._process_item(node)
            item = self._process_meta(item, response.meta)
            item['keyword'] = data['queryContext']['originalQuery']
            item['total'] = data['webPages']['totalEstimatedMatches']
            item['file_urls'] = [item['url']]
            yield item

        # go to next results page

        if self.depth - 1:
            start = data['rankingResponse']['mainline']['items'][-1]
            url = '{}&offset={}'.format(response.request.url, start)
            yield Request(url, meta=response.meta, headers=self.headers)
            self.depth -= 1
