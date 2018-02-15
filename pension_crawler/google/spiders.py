'''spiders.py'''

import json

from datetime import datetime
from urllib.parse import quote_plus, urlencode

from scrapy import Spider, Request
from scrapy.exceptions import NotConfigured

from pension_crawler.items import ResultLoader
from pension_crawler.utils import SpiderMixin

from .settings import SETTINGS


class GoogleSpider(Spider, SpiderMixin):

    '''Parse Google Search API results.'''

    name = 'google'
    custom_settings = SETTINGS

    def __init__(self, crawler, keywords, modifier, depth, site, start_date,
                 end_date, engine_id, api_key, *args, **kwargs):
        '''
        Set queries, modifier, depth, site, start and end date, search engine
        id and api key.
        '''
        super(GoogleSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.keywords = keywords
        self.modifier = modifier
        self.depth = depth
        self.site = site
        self.start_date = start_date
        self.end_date = end_date
        self.engine_id = engine_id
        self.api_key = api_key

    @staticmethod
    def validate_date(date):
        '''Validate date in correct format.'''
        try:
            return datetime.strptime(date, '%Y%m%d')
        except ValueError:
            pass

    @staticmethod
    def parse_spider_settings(settings):
        '''Parse custom spider settings.'''
        start_date = settings.get('START_DATE')
        end_date = settings.get('END_DATE')
        engine_id = settings.get('SEARCH_ENGINE_ID')
        api_key = settings.get('API_KEY')
        if start_date and not GoogleSpider.validate_date(start_date):
            raise NotConfigured('Invalid start date parameter.')
        if end_date and not GoogleSpider.validate_date(end_date):
            raise NotConfigured('Invalid end date parameter.')
        if not engine_id:
            raise NotConfigured('Google search engine ID not set.')
        if not api_key:
            raise NotConfigured('Google API key not set.')
        return start_date, end_date, engine_id, api_key

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        keywords, depth, modifier, site = GoogleSpider.parse_common_settings(
            kwargs, crawler.settings
        )
        spider_settings_data = GoogleSpider.parse_spider_settings(
            crawler.settings
        )
        start_date, end_date, engine_id, api_key = spider_settings_data
        return cls(
            crawler,
            keywords,
            modifier,
            depth,
            site,
            start_date,
            end_date,
            engine_id,
            api_key,
            *args,
            **kwargs
        )

    @property
    def sort(self):
        '''Return search sort by date parameter.'''
        if self.start_date and self.end_date:
            return 'date:r:{}:{}'.format(self.start_date, self.end_date)

    def get_url(self, query):
        '''Return request url.'''
        data = {
            'cx': self.engine_id,
            'key': self.api_key,
            'q': self.get_query(query)
        }
        sort = self.sort
        if sort:
            data['sort'] = sort
        base = 'https://www.googleapis.com/customsearch/v1?{}'
        return base.format(urlencode(data))

    def start_requests(self):
        '''Dispatch requests per keyword.'''
        for keyword in self.keywords:
            yield Request(self.get_url(keyword))

    def process_item(self, node):
        '''Load single result item.'''
        loader = ResultLoader()
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
