'''pipelines.py'''

import os

from datetime import datetime

from scrapy.exceptions import NotConfigured
from scrapy.exporters import CsvItemExporter


class BaseCSVPipeline(object):

    '''Common CSV pipeline functionality.'''

    def __init__(self, output_file, fields_to_export, *args, **kwargs):
        '''Set output file object, fields to export and CSV exporter.'''
        self.file = open(output_file, 'w+b')
        self.exporter = CsvItemExporter(
            self.file, fields_to_export=fields_to_export
        )

    @staticmethod
    def get_settings(settings):
        '''Read spider settings.'''
        output_dir = settings.get('OUTPUT_DIR')
        fields_to_export = settings.get('FIELDS_TO_EXPORT')
        if not output_dir:
            raise NotConfigured('Output directory not set.')
        if not fields_to_export:
            raise NotConfigured('Fields to export not set.')
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M')
        output_file = os.path.join(output_dir, '{}.csv'.format(timestamp))
        return output_file, fields_to_export

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass output file and fields to export to constructor.'''
        output_file, fields_to_export = BaseCSVPipeline.get_settings(
            crawler.settings
        )
        return cls(output_file, fields_to_export, *args, **kwargs)

    def open_spider(self, *args, **kwargs):
        '''Start exporting items on signal.'''
        self.exporter.start_exporting()

    def close_spider(self, *args, **kwargs):
        '''Stop exporting items on signal.'''
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, *args, **kwargs):
        '''Export item to csv file and return item.'''
        self.export_item(item)
        return item

    def get_path(self, item):
        '''Return path or none.'''
        try:
            return item['files'][0]['path']
        except IndexError:
            pass

    def export_item(self, item):
        '''Export row to CSV file.'''
        raise NotImplementedError


class SearchExportDownloadEnabledPipeline(BaseCSVPipeline):

    '''Pipeline that exports items to CSV file when PDF download is enabled.'''

    def export_item(self, item, *args, **kwargs):
        '''Export item to csv file.'''
        data = {
            'keyword': item['keyword'],
            'url': item['url'],
            'title': item['title'],
            'path': self.get_path(item)
        }
        self.exporter.export_item(data)


class SearchExportDownloadDisabledPipeline(BaseCSVPipeline):

    '''Pipeline that exports items to CSV file when PDF download is disabled.'''

    def export_item(self, item, *args, **kwargs):
        '''Export item to csv file.'''
        data = {
            'keyword': item['keyword'],
            'url': item['url'],
            'title': item['title']
        }
        self.exporter.export_item(data)


class SitesExportPipeline(BaseCSVPipeline):

    '''Pipeline that exports items to CSV file from sites crawler.'''

    def export_item(self, item, *args, **kwargs):
        '''Export item to csv file.'''
        data = {
            'parent': item['keyword'],
            'url': item['url'],
            'text': item['title'],
            'path': self.get_path(item)
        }
        self.exporter.export_item(data)
