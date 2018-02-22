'''spiders.py'''

import json

from datetime import datetime
from urllib.parse import urlencode

from scrapy import Spider, Request

from pension_crawler.items import ResultLoader
from pension_crawler.utils import GoogleParser

from .settings import SETTINGS


class GoogleSpider(Spider):

    '''Parse Google Search API results.'''

    # class variables

    name = 'google'
    custom_settings = SETTINGS

    # constructor

    def __init__(self, crawler, input_list, depth, api_key, start_date,
                 end_date, engine_id, *args, **kwargs):
        '''Set queries, depth, search engine id and api key.'''
        super(GoogleSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.input_list = input_list
        self.depth = depth
        self.api_key = api_key
        self.start_date = start_date
        self.end_date = end_date
        self.engine_id = engine_id

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        parser = GoogleParser(kwargs, crawler.settings)
        return cls(
            crawler,
            parser.input_list,
            parser.depth,
            parser.api_key,
            parser.start_date,
            parser.end_date,
            parser.engine_id,
            *args,
            **kwargs
        )

    # private methods

    def _load_item(self, node):
        '''Load single result item.'''
        loader = ResultLoader()
        loader.add_value('url', node['link'])
        loader.add_value('title', node['title'])
        loader.add_value('snippet', node['snippet'])
        loader.add_value('timestamp', datetime.now().isoformat())
        return loader.load_item()

    @property
    def sort(self):
        '''Return search sort by date parameter.'''
        if self.start_date and self.end_date:
            return 'date:r:{}:{}'.format(self.start_date, self.end_date)

    def _get_url(self, query):
        '''Return request url.'''
        data = {'cx': self.engine_id, 'key': self.api_key, 'q': query}
        sort = self.sort
        if sort:
            data['sort'] = sort
        base = 'https://www.googleapis.com/customsearch/v1?{}'
        return base.format(urlencode(data))

    # class method overrides

    def start_requests(self):
        '''Dispatch requests per keyword.'''
        for query in self.input_list:
            yield Request(query)

    def parse(self, response):
        '''Parse search results.'''
        data = json.loads(response.body_as_unicode())
        for node in data.get('items', []):
            item = self._load_item(node)
            item['keyword'] = data['queries']['request'][0]['searchTerms']
            item['total'] = data['searchInformation']['totalResults']
            item['file_urls'] = [item['url']]
            yield item

        # go to next results page

        if self.depth - 1:
            start = data['queries']['nextPage'][0]['startIndex']
            yield Request('{}&start={}'.format(response.request.url, start))
            self.depth -= 1
