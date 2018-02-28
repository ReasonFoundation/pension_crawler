'''settings.py'''

import os

from pension_crawler.settings import DATA_DIR, DOWNLOAD_ENABLED
from pension_crawler.utils import CustomSettings


fields = [
    'keyword', 'url', 'title', 'state', 'system', 'report_type', 'year',
    'page_count', 'path'
]
custom_settings = CustomSettings(DOWNLOAD_ENABLED, fields)


SETTINGS = {

    # Scrapy settings

    'ITEM_PIPELINES': custom_settings.item_pipelines,
    'FIELDS_TO_EXPORT': custom_settings.fields_to_export,

    # Custom settings

    'INPUT_FILE': 'default.csv',
    'INPUT_DIR': os.path.join(DATA_DIR, 'input', 'bing'),
    'OUTPUT_DIR': os.path.join(DATA_DIR, 'output', 'bing'),
    'API_KEY': 'ddb0cdbe8bbe408db2035d4328b7eec9',
}
