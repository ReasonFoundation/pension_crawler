'''pensions.py'''

import json

from datetime import datetime

from scrapy import Spider, Request
from scrapy.exceptions import NotConfigured

from pension_crawler.items import ResultItemLoader


class PensionsSpider(Spider):

    '''Parse Google CSE results.'''

    name = 'pensions'

    def __init__(self, crawler, engine_id, api_key, depth, keywords, *args,
                 **kwargs):
        '''Set search engine id, api key, search depth and keywords.'''
        super(PensionsSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.engine_id = engine_id
        self.api_key = api_key
        self.depth = depth
        self.keywords = keywords

    @staticmethod
    def parse_args(args):
        '''Parse arguments comming from command.'''
        keywords = json.loads(args.pop('keywords'), '[]')
        if not keywords:
            raise NotConfigured('Keyword list not provided as argument.')
        return keywords

    @staticmethod
    def parse_settings(settings):
        '''Parse arguments comming from Scrapy settings.'''
        engine_id = settings.get('SEARCH_ENGINE_ID')
        api_key = settings.get('API_KEY')
        depth = settings.get('SEARCH_DEPTH')
        if not engine_id:
            raise NotConfigured('Search engine ID not set in settings.')
        if not api_key:
            raise NotConfigured('API key not set in settings.')
        return engine_id, api_key, depth

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        keywords = PensionsSpider.parse_args(kwargs)
        engine_id, api_key, depth = PensionsSpider.parse_settings(
            crawler.settings
        )
        return cls(
            crawler, engine_id, api_key, depth, keywords, *args, **kwargs
        )

    def start_requests(self):
        '''Dispatch requests per keyword.'''
        base = 'https://www.googleapis.com/customsearch/v1?cx={}&key={}&q={}&f'\
            'ileType=pdf'
        for keyword in self.keywords:
            url = base.format(self.engine_id, self.api_key, keyword)
            yield Request(url)


    def process_item(self, result):
        '''Load single result item.'''
        loader = ResultItemLoader()
        loader.add_value('url', result['link'])
        loader.add_value('title', result['title'])
        loader.add_value('snippet', result['snippet'])
        loader.add_value('timestamp', datetime.now().isoformat())
        return loader.load_item()

    def parse(self, response):
        '''Parse search results.'''
        data = json.loads(response.body_as_unicode())
        for result in data['items']:
            item = self.process_item(result)
            item.setdefault('total', data['searchInformation']['totalResults'])
            item.setdefault('file_urls', [item['url']])
            yield item
        start = data['queries']['nextPage'][0]['startIndex']
        count = data['queries']['nextPage'][0]['count']
        if (start // count) < self.depth:
            yield Request('{}&start={}'.format(response.request.url, start))
