'''settings.py'''

import os

from pension_crawler.settings import DATA_DIR, NO_DOWNLOAD
from pension_crawler.utils import no_download


SETTINGS = {

    # scrapy settings

    'FILES_STORE': os.path.join(DATA_DIR, 'google', 'downloads'),

    # custom settings

    'OUTPUT_FILE': os.path.join(DATA_DIR, 'google', 'output.csv'),
    'SEARCH_ENGINE_ID': os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
    'API_KEY': os.getenv('GOOGLE_API_KEY'),
    'RESULT_DEPTH': 0,
    'KEYWORD_MODIFIER': 'actuarial valuation'
}

if NO_DOWNLOAD:
    SETTINGS = no_download(SETTINGS)
