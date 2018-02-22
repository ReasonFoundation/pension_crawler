'''spiders.py'''

import json

from datetime import datetime
from urllib.parse import urlencode

from scrapy import Spider, Request

from pension_crawler.items import ResultLoader
from pension_crawler.utils import BingParser

from .settings import SETTINGS


class BingSpider(Spider):

    '''Parse Bing Search API results.'''

    # class variables

    name = 'bing'
    custom_settings = SETTINGS

    # constructor

    def __init__(self, crawler, input_list, depth, api_key, freshness, *args,
                 **kwargs):
        '''Set queries, depth, freshness, and api key.'''
        super(BingSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.input_list = input_list
        self.depth = depth
        self.api_key = api_key
        self.freshness = freshness

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        parser = BingParser(kwargs, crawler.settings)
        return cls(
            crawler,
            parser.input_list,
            parser.depth,
            parser.api_key,
            parser.freshness,
            *args,
            **kwargs
        )

    # properties

    @property
    def headers(self):
        '''Return request headers.'''
        return {'Ocp-Apim-Subscription-Key' : self.api_key}

    # private methods

    def _get_url(self, query):
        '''Return request url.'''
        data = {'q': query}
        if self.freshness:
            data['freshness'] = self.freshness
        base = 'https://api.cognitive.microsoft.com/bing/v7.0/search?{}'
        return base.format(urlencode(data))

    def _load_item(self, node):
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
        for query in self.input_list:
            yield Request(self._get_url(query), headers=self.headers)

    def parse(self, response):
        '''Parse search results.'''
        data = json.loads(response.body_as_unicode())
        for node in data.get('webPages', {}).get('value', []):
            item = self._load_item(node)
            item['keyword'] = data['queryContext']['originalQuery']
            item['total'] = data['webPages']['totalEstimatedMatches']
            item['file_urls'] = [item['url']]
            yield item

        # go to next results page

        if self.depth - 1:
            start = data['rankingResponse']['mainline']['items'][-1]
            yield Request('{}&offset={}'.format(response.request.url, start))
            self.depth -= 1
