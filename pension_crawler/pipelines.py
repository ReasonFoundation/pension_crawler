'''pipelines.py'''

import os

from datetime import datetime

from scrapy.exceptions import NotConfigured
from scrapy.exporters import CsvItemExporter


class CSVPipeline(object):

    '''Export items to CSV.'''

    # constructor

    def __init__(self, path, fields, *args, **kwargs):
        '''Set output file object, fields to export and CSV exporter.'''
        self.file_ = open(path, 'w+b')
        self.exporter = CsvItemExporter(self.file_, fields_to_export=fields)

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass output file and fields to export to constructor.'''
        output_dir = crawler.settings.get('OUTPUT_DIR')
        fields_to_export = crawler.settings.get('FIELDS_TO_EXPORT')
        if not output_dir:
            raise NotConfigured('Output directory not specified.')
        if not fields_to_export:
            raise NotConfigured('Fields to export not specified.')
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M')
        path = os.path.join(output_dir, '{}.csv'.format(timestamp))
        return cls(path, fields_to_export, *args, **kwargs)

    # private methods

    def _path(self, item):
        '''Return path or none.'''
        try:
            return item['files'][0]['path']
        except IndexError:
            return ''

    def _export(self, item):
        '''Export row to CSV file.'''
        data = {}
        for key in self.exporter.fields_to_export:
            if key == 'path':
                data[key] = self._path(item)
            else:
                data[key] = item[key]
        self.exporter.export_item(data)

    # overriden class methods

    def open_spider(self, *args, **kwargs):
        '''Start exporting items on signal.'''
        self.exporter.start_exporting()

    def close_spider(self, *args, **kwargs):
        '''Stop exporting items on signal.'''
        self.exporter.finish_exporting()
        self.file_.close()

    def process_item(self, item, *args, **kwargs):
        '''Export item to csv file and return item.'''
        self._export(item)
        return item
