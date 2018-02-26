'''utils.py'''

import csv
import os

import tldextract

from scrapy import Spider
from scrapy.exceptions import NotConfigured


class BaseSpider(Spider):

    # static methods

    @staticmethod
    def _data(settings):
        input_dir = settings.get('INPUT_DIR')
        input_file = settings.get('input_file')
        if not input_dir:
            raise NotConfigured('Input directory not specified.')
        if not input_file:
            raise NotConfigured('Input file not specified.')
        try:
            with open(os.path.join(input_dir, input_file), 'r') as file_:
                reader = csv.DictReader(file_)
                return list(reader)
        except IOError:
            raise NotConfigured('Error reading input data.')

    # private methods

    def _query(self, row):
        '''Return search query.'''
        site = row.get('site')
        if site:
            extract = tldextract.extract(site)
            site = 'site:{}.{}'.format(extract.domain, extract.suffix)
        query = [row.get('keyword'), row.get('modifier'), site, 'filetype:pdf']
        return ' '.join([i for i in query if i])

    def _meta(self, row):
        '''Return request meta dictionary.'''
        return {
            'state': row.get('state', ''),
            'system': row.get('system', ''),
            'report_type': row.get('report_type', '')
        }

    def _process_meta(self, item, meta):
        '''Merge meta dict with item.'''
        item['state'] = meta['state']
        item['system'] = meta['system']
        item['report_type'] = meta['report_type']
        return item


class CustomSettings(object):

    '''Return specific settings object if PDF download is enabled or not.'''

    # constructor

    def __init__(self, download_enabled, fields):
        '''Set download.'''
        self.download_enabled = download_enabled
        self.fields = fields

    # properties

    @property
    def item_pipelines(self):
        '''Return item pipelines.'''
        if not self.download_enabled:
            return {
                'pension_crawler.pipelines.SearchExportDownloadDisabledPipelin'
                    'e': 300
            }
        return {
            'scrapy.pipelines.files.FilesPipeline': 1,
            'pension_crawler.pipelines.SearchExportDownloadEnabledPipeline': 300
        }

    @property
    def fields_to_export(self):
        '''Return fields to export'''
        if not self.download_enabled:
            self.fields.remove('path')
        return self.fields
