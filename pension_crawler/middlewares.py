'''middlewares.py'''

import logging

import tldextract

from scrapy.exceptions import NotConfigured, IgnoreRequest


class RequestBlacklistMiddleware(object):

    '''Block requests to url based on an input file.'''

    def __init__(self, blacklist, *args, **kwargs):
        '''Set start urls.'''
        super(RequestBlacklistMiddleware, self).__init__(*args, **kwargs)
        self.blacklist = blacklist

    @staticmethod
    def parse_settings(settings):
        '''Read blacklist file from settings.'''
        blacklist_file = settings.get('BLACKLIST_FILE')
        if not blacklist_file:
            raise NotConfigured('Blacklist file not set.')
        return blacklist_file

    @staticmethod
    def parse_blacklist(path):
        '''Read blacklisted urls from file.'''
        blacklist = []
        try:
            with open(path, 'r') as file_:
                for line in file_.readlines():
                    blacklist.append(line.strip())
        except IOError:
            raise NotConfigured('Could not read blacklist file.')
        if not blacklist:
            logging.warn('Blacklisted url list is empty')
        return blacklist

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass user agent list to constructor.'''
        blacklist_file = RequestBlacklistMiddleware.parse_settings(
            crawler.settings
        )
        blacklist = RequestBlacklistMiddleware.parse_blacklist(blacklist_file)
        return cls(blacklist, *args, **kwargs)

    def process_request(self, request, *args, **kwargs):
        '''Ignore requests to domains specified in blacklist file.'''
        parsed = tldextract.extract(request.url)
        domain = '.'.join((parsed.domain, parsed.suffix))
        if domain in self.blacklist:
            raise IgnoreRequest()
