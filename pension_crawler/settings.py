'''settings.py'''

import os


BOT_NAME = 'pension_crawler'
SPIDER_MODULES = ['pension_crawler.spiders']
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')
API_KEY = os.getenv('API_KEY')
