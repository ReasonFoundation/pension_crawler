'''settings.py'''

import os


# Development settings

HTTPCACHE_ENABLED = True


# Custom settings

DATA_DIR = os.path.join(os.getcwd(), 'data')
BLACKLIST_FILE = os.path.join(DATA_DIR, 'blacklist.txt')
DOWNLOAD_ENABLED = True
DEPTH = 1
PAGE_COUNT = 1


# Scrapy settings

BOT_NAME = 'pension_crawler'
LOG_LEVEL = 'INFO'
SPIDER_MODULES = [
    'pension_crawler.google', 'pension_crawler.bing', 'pension_crawler.sites'
]
DOWNLOADER_MIDDLEWARES = {
    'pension_crawler.middlewares.BlacklistMiddleware': 400
}
FILES_STORE = os.path.join(DATA_DIR, 'downloads')
COOKIES_ENABLED = False,
RETRY_ENABLED = False,
DOWNLOAD_TIMEOUT = 90,
DOWNLOAD_DELAY = 0.5
