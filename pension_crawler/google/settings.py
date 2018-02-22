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
    'start_date': None,  # Required format: YYYYMMDD
    'end_date': None,  # Required format: YYYYMMDD
    'depth': 0,

    'INPUT_DIR': os.path.join(DATA_DIR, 'input', 'google'),
    'OUTPUT_DIR': os.path.join(DATA_DIR, 'output', 'google'),

    # Secret settings

    'SEARCH_ENGINE_ID': SECRETS['GOOGLE_SEARCH_ENGINE_ID'],
    'API_KEY': SECRETS['GOOGLE_API_KEY'],

    # Scrapy settings

    'ITEM_PIPELINES': settings.item_pipelines,
    'FIELDS_TO_EXPORT': settings.fields_to_export,
    'COOKIES_ENABLED': False,
    'RETRY_ENABLED': False,
    'DOWNLOAD_TIMEOUT': 90,
    'DOWNLOAD_DELAY': 0.5
}
