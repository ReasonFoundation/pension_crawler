'''pensions.py'''

import json

from datetime import datetime

from scrapy import Spider, Request
from scrapy.exceptions import NotConfigured

from pension_crawler.items import ResultItemLoader


class PensionsSpider(Spider):

    '''Parse Google CSE results.'''

    name = 'pensions'

    def __init__(self, crawler, keywords, engine_id, api_key, depth, *args,
                 **kwargs):
        '''Set search engine id, api key, search depth and keywords.'''
        super(PensionsSpider, self).__init__(*args, **kwargs)
        self.crawler = crawler
        self.keywords = keywords
        self.engine_id = engine_id
        self.api_key = api_key
        self.depth = depth

    @staticmethod
    def parse_keywords(path):
        '''Read search keywrods from input file.'''
        keywords = []
        try:
            with open(path, 'r') as file_:
                for line in file_.readlines():
                    keywords.append(line.strip().lower())
        except IOError:
            raise NotConfigured('Could not read input file.')
        if not keywords:
            raise NotConfigured('Keyword list is empty.')
        return keywords

    @staticmethod
    def parse_settings(settings):
        '''Read search keywrods from input file.'''
        input_file = settings.get('INPUT_FILE')
        engine_id = settings.get('SEARCH_ENGINE_ID')
        api_key = settings.get('API_KEY')
        depth = settings.get('SEARCH_DEPTH')
        if not input_file:
            raise NotConfigured('Input file not set.')
        if not engine_id:
            raise NotConfigured('Search engine ID not set.')
        if not api_key:
            raise NotConfigured('API key not set.')
        return input_file, engine_id, api_key, depth

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass settings to constructor.'''
        input_file, engine_id, api_key, depth = PensionsSpider.parse_settings(
            crawler.settings
        )
        keywords = PensionsSpider.parse_keywords(input_file)
        return cls(
            crawler, keywords, engine_id, api_key, depth, *args, **kwargs
        )

    def start_requests(self):
        '''Dispatch requests per keyword.'''
        base = 'https://www.googleapis.com/customsearch/v1?cx={}&key={}&q={} a'\
            'ctuarial valuation&fileType=pdf'
        for keyword in self.keywords:
            url = base.format(self.engine_id, self.api_key, keyword)
            yield Request(url)

    def process_result(self, result):
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
            item = self.process_result(result)
            item.setdefault(
                'keyword', data['queries']['request'][0]['searchTerms']
            )
            item.setdefault('total', data['searchInformation']['totalResults'])
            item.setdefault('file_urls', [item['url']])
            yield item
        start = data['queries']['nextPage'][0]['startIndex']
        count = data['queries']['nextPage'][0]['count']
        if (start // count) < self.depth:
            yield Request('{}&start={}'.format(response.request.url, start))
