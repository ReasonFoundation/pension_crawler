'''pipelines.py'''

from scrapy.exceptions import NotConfigured
from scrapy.exporters import CsvItemExporter


class ResultItemCSVExportPipeline(object):

    '''Pipeline that modifies and exports items to CSV file.'''

    def __init__(self, output_file, fields_to_export, *args, **kwargs):
        '''Set output file object, fields to export and CSV exporter.'''
        self.file = open(output_file, 'w+b')
        self.exporter = CsvItemExporter(
            self.file, fields_to_export=fields_to_export
        )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass output file to constructor and connect signals.'''
        output_file = crawler.settings.get('OUTPUT_FILE')
        fields_to_export = crawler.settings.get('FIELDS_TO_EXPORT')
        if not output_file:
            raise NotConfigured('Output file not set.')
        if not fields_to_export:
            raise NotConfigured('Fields to export not set.')
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
        try:
            path = item['files'][0]['path']
        except IndexError:
            path = None
        data = {
            'keyword': item['keyword'],
            'url': item['url'],
            'title': item['title'],
            'path': path
        }
        self.exporter.export_item(data)
        return item
