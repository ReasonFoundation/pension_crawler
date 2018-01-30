'''settings.py'''

import os


# scrapy settings

BOT_NAME = 'pension_crawler'
SPIDER_MODULES = ['pension_crawler.spiders']
ITEM_PIPELINES = {
    'scrapy.pipelines.files.FilesPipeline': 1,
    'pension_crawler.pipelines.ResultItemCSVExportPipeline': 900
}
FILES_STORE = os.path.join(os.getcwd(), 'data', 'downloads')
FIELDS_TO_EXPORT = ['keyword', 'url', 'title', 'path']


# custom settings

INPUT_FILE = os.path.join(os.getcwd(), 'data', 'input.csv')
OUTPUT_FILE = os.path.join(os.getcwd(), 'data', 'output.csv')

SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
API_KEY = os.getenv('API_KEY')
SEARCH_DEPTH = int(os.getenv('SEARCH_DEPTH', 1))
