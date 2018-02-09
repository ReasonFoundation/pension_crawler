'''settings.py'''

import os

from pension_crawler.settings import DATA_DIR, NO_DOWNLOAD
from pension_crawler.utils import no_download


SETTINGS = {

    # scrapy settings

    'FILES_STORE': os.path.join(DATA_DIR, 'bing', 'downloads'),

    # custom settings

    'OUTPUT_FILE': os.path.join(DATA_DIR, 'bing', 'output.csv'),
    'API_KEY': os.getenv('BING_API_KEY'),
    'RESULT_DEPTH': 0,
    'KEYWORD_MODIFIER': 'actuarial valuation'
}

if NO_DOWNLOAD:
    SETTINGS = no_download(SETTINGS)
