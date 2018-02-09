'''pipelines.py'''

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
    def parse_settings(settings):
        '''Read spider settings.'''
        output_file = settings.get('OUTPUT_FILE')
        fields_to_export = settings.get('FIELDS_TO_EXPORT')
        if not output_file:
            raise NotConfigured('Output file not set.')
        if not fields_to_export:
            raise NotConfigured('Fields to export not set.')
        return output_file, fields_to_export

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass output file and fields to export to constructor.'''
        output_file, fields_to_export = BaseCSVPipeline.parse_settings(
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

    def export_item(self, item):
        '''Export row to CSV file.'''
        raise NotImplementedError


class PDFDownloadPipeline(BaseCSVPipeline):

    '''Pipeline that exports items to CSV file when PDF download is enabled.'''

    def export_item(self, item, *args, **kwargs):
        '''Export item to csv file.'''
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


class PDFNoDownloadPipeline(BaseCSVPipeline):

    '''Pipeline that exports items to CSV file when PDF download is disabled.'''

    def export_item(self, item, *args, **kwargs):
        '''Export item to csv file.'''
        data = {
            'keyword': item['keyword'],
            'url': item['url'],
            'title': item['title']
        }
        self.exporter.export_item(data)
