'''settings.py'''

import os


# Development settings. Comment out when in production.

HTTPCACHE_ENABLED = True


# Scrapy settings

BOT_NAME = 'pension_crawler'
SPIDER_MODULES = ['pension_crawler.google', 'pension_crawler.bing']
DOWNLOADER_MIDDLEWARES = {
    'pension_crawler.middlewares.RequestBlacklistMiddleware': 400
}
ITEM_PIPELINES = {
    'scrapy.pipelines.files.FilesPipeline': 1,
    'pension_crawler.pipelines.ResultItemCSVExportPipeline': 900
}
FIELDS_TO_EXPORT = ['keyword', 'url', 'title', 'path']
DOWNLOAD_DELAY = 1  # slow down crawling


# Custom settings

DATA_DIR = os.path.join(os.getcwd(), 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'input.csv')
BLACKLIST_FILE = os.path.join(DATA_DIR, 'blacklist.csv')

RESULT_DEPTH = 0  # visit first page only
