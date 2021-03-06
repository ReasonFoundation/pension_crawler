'''settings.py'''

import os

from datetime import datetime


# Custom settings

DATA_DIR = os.path.join(os.getcwd(), 'data')
LOG_NAME = 'crawl-{}.log'.format(datetime.now().strftime('%Y-%m-%d-%H-%M'))
TEMP_DIR = os.path.join(DATA_DIR, 'temp')
BLACKLIST_FILE = os.path.join(DATA_DIR, 'blacklist.csv')
DOWNLOAD_ENABLED = True
DEPTH = 1
PAGE_COUNT = 1
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like '
    'Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like G'
    'ecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like '
    'Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/'
    '57.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML,'
    ' like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML'
    ', like Gecko) Version/11.0.2 Safari/604.4.7',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML,'
    ' like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like G'
    'ecko) Chrome/63.0.3239.84 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/5'
    '7.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57'
    '.0'
]


# Scrapy settings

BOT_NAME = 'pension_crawler'
LOG_LEVEL = 'DEBUG'
LOG_FILE = os.path.join(DATA_DIR, 'logs', LOG_NAME)
SPIDER_MODULES = [
    'pension_crawler.google', 'pension_crawler.bing', 'pension_crawler.sites'
]
DOWNLOADER_MIDDLEWARES = {
    'pension_crawler.middlewares.BlacklistMiddleware': 400,
    'pension_crawler.middlewares.UserAgentMiddleware': 410,
}
FILES_STORE = os.path.join(DATA_DIR, 'downloads')
COOKIES_ENABLED = False
DOWNLOAD_DELAY = 1
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 604800
