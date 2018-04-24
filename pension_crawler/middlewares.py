'''middlewares.py'''

import logging
import random

import tldextract

from scrapy.exceptions import NotConfigured, IgnoreRequest


# logging

logger = logging.getLogger(__name__)


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
        domain = '.'.join((parsed.domain, parsed.suffix))
        if domain in self.data:
            message = 'Blacklist middleware - Request to {} filtered.'
            logger.info(message.format(domain))
            raise IgnoreRequest()


class UserAgentMiddleware(object):

    '''Random user agent on every request.'''

    # constructor

    def __init__(self, user_agents, *args, **kwargs):
        '''Set user agent list.'''
        super(UserAgentMiddleware, self).__init__(*args, **kwargs)
        self.user_agents = user_agents

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass data to constructor.'''
        user_agents = crawler.settings.get('USER_AGENTS')
        if not user_agents:
            raise NotConfigured('User agent list is empty.')
        return cls(user_agents, *args, **kwargs)

    # properties

    @property
    def user_agent(self):
        '''Get random user agent from list.'''
        return random.choice(self.user_agents)

    # overriden class methods

    def process_request(self, request, *args, **kwargs):
        '''Set random user agent in request headers.'''
        request.headers.setdefault('User-Agent', self.user_agent)
