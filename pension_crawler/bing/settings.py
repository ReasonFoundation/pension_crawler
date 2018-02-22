'''settings.py'''

import os

from pension_crawler.secrets import SECRETS
from pension_crawler.settings import DATA_DIR
from pension_crawler.utils import Settings


# set download to False to disable PDF downloading from search results

DOWNLOAD = True
settings = Settings(DOWNLOAD)

SETTINGS = {

    # Custom settings

    'keyword_file': 'keywords.txt',
    'site_file': 'sites.txt',
    'modifier': 'actuarial valuation',
    'site': None,
    'freshness': None,  # Possible values: Day, Week, Month
    'depth': 0,

    'INPUT_DIR': os.path.join(DATA_DIR, 'input', 'bing'),
    'OUTPUT_DIR': os.path.join(DATA_DIR, 'output', 'bing'),

    # Secret settings

    'API_KEY': SECRETS['BING_API_KEY'],

    # Scrapy settings

    'ITEM_PIPELINES': settings.item_pipelines,
    'FIELDS_TO_EXPORT': settings.fields_to_export,
    'COOKIES_ENABLED': False,
    'RETRY_ENABLED': False,
    'DOWNLOAD_TIMEOUT': 90,
    'DOWNLOAD_DELAY': 0.5
}
