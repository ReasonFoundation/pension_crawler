'''pipelines.py'''

import logging
import os

from datetime import datetime

from scrapy.exceptions import NotConfigured
from scrapy.exporters import CsvItemExporter
from twisted.internet import reactor
from twisted.internet.defer import Deferred, inlineCallbacks

from pension_crawler.utils import PDFParser


# logging

logger = logging.getLogger(__name__)


class BasePipeline(object):

    '''Common functionality for pipelines.'''

    def _path(self, item):
        '''Return path or none.'''
        try:
            return item['files'][0]['path']
        except IndexError:
            pass


class IsDownloadedPipeline(BasePipeline):

    '''A pipeline for determining if PDF is downloaded or not.'''

    # constructor

    def __init__(self, fnames, *args, **kwargs):
        '''Set file names set.'''
        self.fnames = fnames

    @classmethod
    def from_crawler(cls, crawler):
        '''Pass data to constructor.'''
        fnames_dir = crawler.settings.get('FILES_STORE')
        if not fnames_dir:
            raise NotConfigured('Download directory not specified.')
        fnames_dir = os.path.join(fnames_dir, 'full')
        fnames = {f.split('.')[0] for f in os.listdir(fnames_dir)}
        return cls(fnames)

    def process_item(self, item, *args, **kwargs):
        '''Check if PDF filen name hash is in seen hashes.'''
        path = self._path(item)
        if not path:
            item['downloaded'] = ''
        else:
            fname = path.split('.')[0].replace('full/', '')
            item['downloaded'] = fname not in self.fnames
        return item


class PDFPipeline(BasePipeline):

    '''A pipeline for parsing year from PDF files.'''

    # constructor

    def __init__(self, count, data_dir, temp_dir, *args, **kwargs):
        '''Set page count and temporary directory.'''
        self.count = count
        self.data_dir = data_dir
        self.temp_dir = temp_dir

    # class methods

    @classmethod
    def from_crawler(cls, crawler):
        '''Pass data to constructor.'''
        page_count = crawler.settings.get('PAGE_COUNT')
        data_dir = crawler.settings.get('FILES_STORE')
        temp_dir = crawler.settings.get('TEMP_DIR')
        if not page_count:
            raise NotConfigured('Page count not specified.')
        if not temp_dir:
            raise NotConfigured('Temporary directory not specified.')
        return cls(page_count, data_dir, temp_dir)

    # private method

    def _parse(self, path, deferred):
        '''Parse PDF wrapper.'''
        parser = PDFParser(path, self.count, self.temp_dir)
        parser.parse()
        reactor.callFromThread(deferred.callback, (parser.year, parser.count))

    # class method overrides

    @inlineCallbacks
    def process_item(self, item, spider):
        '''Append results from PDF parser to item.'''
        path = self._path(item)
        if not path:
            return item
        path = os.path.join(self.data_dir, path)
        deferred = Deferred()
        reactor.callInThread(self._parse, path, deferred)
        year, count = yield deferred
        item['year'] = year
        item['page_count'] = count
        return item


class CSVPipeline(BasePipeline):

    '''Export items to CSV.'''

    # constructor

    def __init__(self, output_dir, fname, fields, *args, **kwargs):
        '''Set output file object and CSV exporter.'''
        self.fname = fname
        self.file_ = open(os.path.join(output_dir, fname), 'w+b')
        self.exporter = CsvItemExporter(self.file_, fields_to_export=fields)

    # class methods

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        '''Pass data to constructor.'''
        output_dir = crawler.settings.get('OUTPUT_DIR')
        fields_to_export = crawler.settings.get('FIELDS_TO_EXPORT')
        if not output_dir:
            raise NotConfigured('Output directory not specified.')
        if not fields_to_export:
            raise NotConfigured('Fields to export not specified.')
        fname = '{}.csv'.format(datetime.now().strftime('%Y-%m-%d-%H-%M'))
        return cls(output_dir, fname, fields_to_export, *args, **kwargs)

    # private methods

    def _export(self, item):
        '''Export row to CSV file.'''
        data = {}
        for key in self.exporter.fields_to_export:
            if key == 'path':
                data['path'] = os.path.join('downloads', self._path(item))
            else:
                data[key] = item.get(key)
        self.exporter.export_item(data)

    # overriden class methods

    def open_spider(self, *args, **kwargs):
        '''Start exporting items on signal.'''
        message = 'CSV pipeline - Started exporting to file: {}'
        logger.info(message.format(self.fname))
        self.exporter.start_exporting()

    def close_spider(self, *args, **kwargs):
        '''Stop exporting items on signal.'''
        self.exporter.finish_exporting()
        self.file_.close()
        message = 'CSV pipeline - Finished exporting to file: {}'
        logger.info(message.format(self.fname))

    def process_item(self, item, *args, **kwargs):
        '''Export item to csv file and return item.'''
        self._export(item)
        return item
