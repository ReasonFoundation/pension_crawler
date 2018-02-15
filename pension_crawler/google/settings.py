'''settings.py'''

import os

from pension_crawler.settings import DATA_DIR

from pension_crawler.secrets import SECRETS
from pension_crawler.utils import get_download_settings


# set download to False to disable PDF downloading from search results

DOWNLOAD = True

item_pipelines, fields_to_export = get_download_settings(DOWNLOAD)

SETTINGS = {

    # Custom settings

    'INPUT_FILE': os.path.join(DATA_DIR, 'input', 'google', 'default.csv'),
    'OUTPUT_DIR': os.path.join(DATA_DIR, 'output', 'google'),
    'KEYWORD_MODIFIER': 'actuarial valuation',
    'SITE': None,
    'START_DATE': None,  # Required format: YYYYMMDD
    'END_DATE': None,  # Required format: YYYYMMDD
    'RESULT_DEPTH': 0,

    # Secret settings

    'SEARCH_ENGINE_ID': SECRETS['GOOGLE_SEARCH_ENGINE_ID'],
    'API_KEY': SECRETS['GOOGLE_API_KEY'],

    # Scrapy settings

    'ITEM_PIPELINES': item_pipelines,
    'FIELDS_TO_EXPORT': fields_to_export,
    'COOKIES_ENABLED': False,
    'REDIRECT_ENABLED': False,
    'RETRY_ENABLED': False,
    'DOWNLOAD_TIMEOUT': 90,
    'DOWNLOAD_DELAY': 0.5
}
