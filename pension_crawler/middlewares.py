'''middlewares.py'''

import tldextract

from scrapy.exceptions import NotConfigured, IgnoreRequest


class BlacklistMiddleware(object):

    '''Block requests to url based on an input file.'''

    # constructor

    def __init__(self, data, *args, **kwargs):
        '''Set data.'''
        super(BlacklistMiddleware, self).__init__(*args, **kwargs)
        self.data = data

    # static methods

    @staticmethod
    def _data(path):
        '''Read blacklisted urls from file.'''
        try:
            with open(path, 'r') as file_:
                return [l.strip() for l in file_.readlines()]
        except IOError:
            raise NotConfigured('Error reading blacklist data.')

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass data to constructor.'''
        file_ = crawler.settings.get('BLACKLIST_FILE')
        if not file_:
            raise NotConfigured('Blacklist file not specified.')
        return cls(BlacklistMiddleware._data(file_), *args, **kwargs)

    # overriden class methods

    def process_request(self, request, *args, **kwargs):
        '''Ignore requests to domains specified in blacklist file.'''
        parsed = tldextract.extract(request.url)
        if '.'.join((parsed.domain, parsed.suffix)) in self.data:
            raise IgnoreRequest()
