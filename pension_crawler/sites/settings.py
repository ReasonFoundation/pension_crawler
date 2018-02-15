'''settings.py'''

import os

from pension_crawler.settings import DATA_DIR


SETTINGS = {

    # Custom settings

    'INPUT_FILE': os.path.join(DATA_DIR, 'input', 'sites', 'default.txt'),
    'OUTPUT_DIR': os.path.join(DATA_DIR, 'output', 'sites'),

    # Scrapy settings

    'ITEM_PIPELINES': {
        'scrapy.pipelines.files.FilesPipeline': 1,
        'pension_crawler.pipelines.SitesExportPipeline': 300
    },
    'FIELDS_TO_EXPORT': ['parent', 'url', 'text']
}
