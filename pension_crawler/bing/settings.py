'''settings.py'''

import os

from pension_crawler.settings import DATA_DIR


SETTINGS = {

    # scrapy settings

    'FILES_STORE': os.path.join(DATA_DIR, 'bing', 'downloads'),

    # custom settings

    'OUTPUT_FILE': os.path.join(DATA_DIR, 'bing', 'output.csv'),
    'API_KEY': os.getenv('BING_API_KEY')
}
