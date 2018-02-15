'''spiders.py'''

import json

from datetime import datetime
from urllib.parse import quote_plus, urlencode

from scrapy import Spider, Request
from scrapy.exceptions import NotConfigured

from pension_crawler.items import ResultLoader
from pension_crawler.utils import SpiderMixin

from .settings import SETTINGS


class BingSpider(Spider, SpiderMixin):

    '''Parse Bing Search API results.'''

    name = 'bing'
    custom_settings = SETTINGS

    def __init__(self, crawler, keywords, modifier, depth, freshness, api_key,
                 *args, **kwargs):
        '''Set queries, modifier, depth, freshness and api key.'''
        super(BingSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.keywords = keywords
        self.modifier = modifier
        self.depth = depth
        self.freshness = freshness
        self.api_key = api_key

    @staticmethod
    def validate_freshness(freshness):
        '''Validate freshness in correct format.'''
        return freshness in ['Day', 'Week', 'Month']

    @staticmethod
    def parse_spider_settings(settings):
        '''Parse custom spider settings.'''
        freshness = settings.get('FRESHNESS')
        api_key = settings.get('API_KEY')
        if not BingSpider.validate_freshness(freshness):
            raise NotConfigured('Invalid freshness parameter.')
        if not api_key:
            raise NotConfigured('Google API key not set.')
        return freshness, api_key

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        keywords, depth, modifier = BingSpider.parse_common_settings(
            kwargs, crawler.settings
        )
        freshness, api_key = BingSpider.parse_spider_settings(crawler.settings)
        return cls(
            crawler,
            keywords,
            modifier,
            depth,
            freshness,
            api_key,
            *args,
            **kwargs
        )

    @property
    def headers(self, query):
        '''Return request headers.'''
        return {'Ocp-Apim-Subscription-Key' : self.api_key}

    def get_url(self, query):
        '''Return request url.'''
        data = {'q': self.get_query(query), 'freshness': self.freshness}
        base = 'https://api.cognitive.microsoft.com/bing/v7.0/search?q={}'
        return base.format(urlencode(data))

    def start_requests(self):
        '''Dispatch requests per keyword.'''
        for keyword in self.keywords:
            yield Request(self.get_url(keyword), headers=self.headers)

    def process_item(self, node):
        '''Load single result item.'''
        loader = ResultLoader()
        loader.add_value('url', node['url'])
        loader.add_value('title', node['name'])
        loader.add_value('snippet', node['snippet'])
        loader.add_value('timestamp', datetime.now().isoformat())
        return loader.load_item()

    def parse(self, response):
        '''Parse search results.'''
        data = json.loads(response.body_as_unicode())
        for node in data.get('webPages', {}).get('value', []):
            item = self.process_item(node)
            item['keyword'] = data['queryContext']['originalQuery']
            item['total'] = data['webPages']['totalEstimatedMatches']
            item['file_urls'] = [item['url']]
            yield item

        # go to next results page

        if self.depth:
            start = data['rankingResponse']['mainline']['items'][-1]
            yield Request('{}&offset={}'.format(response.request.url, start))
            self.depth -= 1
