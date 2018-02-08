'''spiders.py'''

import json

from datetime import datetime
from urllib.parse import quote_plus

from scrapy import Spider, Request
from scrapy.exceptions import NotConfigured

from pension_crawler.items import ResultItemLoader
from pension_crawler.utils import SpiderMixin

from .settings import SETTINGS


class GoogleSpider(Spider, SpiderMixin):

    '''Parse Google Search API results.'''

    name = 'google'
    custom_settings = SETTINGS

    def __init__(self, crawler, keywords, engine_id, api_key, depth, *args,
                 **kwargs):
        '''Set search engine id, api key, search depth and keywords.'''
        super(GoogleSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.keywords = keywords
        self.engine_id = engine_id
        self.api_key = api_key
        self.depth = depth

    @staticmethod
    def parse_spider_settings(settings):
        '''Parse custom spider settings.'''
        engine_id = settings.get('SEARCH_ENGINE_ID')
        api_key = settings.get('API_KEY')
        if not engine_id:
            raise NotConfigured('Google search engine ID not set.')
        if not api_key:
            raise NotConfigured('Google API key not set.')
        return engine_id, api_key

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        input_file, depth = GoogleSpider.parse_settings(crawler.settings)
        engine_id, api_key, = GoogleSpider.parse_spider_settings(
            crawler.settings
        )
        keywords = GoogleSpider.parse_keywords(input_file)
        return cls(
            crawler, keywords, engine_id, api_key, depth, *args, **kwargs
        )

    def start_requests(self):
        '''Dispatch requests per keyword.'''
        modifier = 'actuarial valuation filetype:pdf'
        base = 'https://www.googleapis.com/customsearch/v1?cx={}&key={}&q={}'
        for keyword in self.keywords:
            keyword = quote_plus('{} {}'.format(keyword, modifier))
            url = base.format(self.engine_id, self.api_key, keyword)
            yield Request(url)

    def process_item(self, node):
        '''Load single result item.'''
        loader = ResultItemLoader()
        loader.add_value('url', node['link'])
        loader.add_value('title', node['title'])
        loader.add_value('snippet', node['snippet'])
        loader.add_value('timestamp', datetime.now().isoformat())
        return loader.load_item()

    def parse(self, response):
        '''Parse search results.'''
        data = json.loads(response.body_as_unicode())
        for result in data.get('items', []):
            item = self.process_item(result)
            item['keyword'] = data['queries']['request'][0]['searchTerms']
            item['total'] = data['searchInformation']['totalResults']
            item['file_urls'] = [item['url']]
            yield item

        # go to next results page

        if self.depth:
            start = data['queries']['nextPage'][0]['startIndex']
            yield Request('{}&start={}'.format(response.request.url, start))
            self.depth -= 1
