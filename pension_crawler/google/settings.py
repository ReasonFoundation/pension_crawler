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

    'INPUT_DIR': os.path.join(DATA_DIR, 'input', 'google'),
    'OUTPUT_DIR': os.path.join(DATA_DIR, 'output', 'google'),
    'SEARCH_ENGINE_ID': 'AIzaSyDQmBGbFQBXdBCz94lNWHV86KEdrAFdQfw',
    'API_KEY': '006550828608930697575:rdedpbbuy94',
}
