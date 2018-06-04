'''utils.py'''

import csv
import errno
import logging
import os
import re
import uuid

import textract
import tldextract

from PyPDF2 import PdfFileReader, PdfFileWriter
from PyPDF2.utils import PdfReadError
from scrapy import Spider
from scrapy.exceptions import NotConfigured


# logging

logger = logging.getLogger(__name__)


class PDFCutter(object):

    '''Cut PDF to target page count.'''

    # constructor

    def __init__(self, path, count, temp_dir):
        '''Set PDF path, target page count and temporary directory.'''
        self.path = path
        self.count = count
        self.temp_dir = temp_dir
        self.original = None

    # properties

    @property
    def temp_file(self):
        '''Return full path to temporary file.'''
        fname = '{}.pdf'.format(uuid.uuid4().hex)
        return os.path.join(self.temp_dir, fname)

    # private methods

    def _write(self, reader, path, count):
        '''Write PDF to temporary directory.'''
        writer = PdfFileWriter()
        for i in range(count):
            writer.addPage(reader.getPage(i))
        with open(path, 'wb') as file_:
            writer.write(file_)

    # public methods

    def cut(self):
        '''Cut and write if PDF has more pages than target.'''
        with open(self.path, 'rb') as file_:
            reader = PdfFileReader(file_)
            self.original = reader.getNumPages()
            if self.count < self.original:
                message = 'PDF cutter - Resizing PDF {} to {} pages.'
                logger.info(message.format(self.path, self.count))
                path = self.temp_file
                self._write(reader, path, self.count)
                self.path = path
                message = 'PDF cutter - Created temporary PDF: {}.'
                logger.info(message.format(self.path))
            else:
                self.count = self.original
                message = 'PDF cutter - PDF {} not modified.'
                logger.info(message.format(self.path))


class PDFReader(object):

    '''Extract text from PDF.'''

    # constructor

    def __init__(self, path, count):
        '''Set path and page count.'''
        self.path = path
        self.count = count
        self.text = ''

    # private methods

    def _pypdf2(self):
        '''Read text from PDF using pypdf2.'''
        message = 'PDF reader - Trying to parse PDF {} text using PyPDF2.'
        logger.info(message.format(self.path))
        text = []
        with open(self.path, 'rb') as file_:
            reader = PdfFileReader(file_)
            for i in range(self.count):
                text.append(reader.getPage(i).extractText())
        return '\n'.join(text).strip()

    def _textract(self):
        '''Read text from PDF using textract.'''
        message = 'PDF reader - Trying to parse PDF {} text using Textract.'
        logger.info(message.format(self.path))
        text = textract.process(self.path, method='tesseract', language='eng')
        return text.decode('utf-8').strip()

    # public methods

    def read(self):
        '''Read text from PDF.'''
        self.text = self._pypdf2()
        if not self.text:
            message = 'PDF reader - Failed to parse PDF {} text using PyPDF2.'
            logger.info(message.format(self.path))
            self.text = self._textract()
        if not self.text:
            message = 'PDF reader - Failed to parse PDF {} text using Textract.'
            logger.info(message.format(self.path))
            message = 'PDF reader - Text not found in PDF: {}.'
            logger.info(message.format(self.path))
            return


class PDFParser(object):

    '''Extract page count and year from PDF.'''

    # constructor

    def __init__(self, path, count, temp_dir):
        '''Set path, page count and temporary directory..'''
        self.path = path
        self.count = count
        self.temp_dir = temp_dir
        self.year = None

    # private methods

    def _year(self, text):
        '''Match year with regex.'''
        try:
            value = re.search(r'(19|20)\d{2}', text).group()
            message = 'PDF parser - Found PDF file {} year: {}.'
            logger.info(message.format(self.path, value))
            return value
        except AttributeError:
            message = 'PDF parser - Failed to find PDF file {} year.'
            logger.info(message.format(self.path))
            pass

    def _remove(self, path):
        '''Remove file if it exists.'''
        try:
            os.remove(path)
        except OSError:
            pass

    # public methods

    def parse(self):
        '''Parse year from PDF file.'''
        try:
            cutter = PDFCutter(self.path, self.count, self.temp_dir)
            cutter.cut()
        except PdfReadError:
            message = 'PDF parser - Failed to read PDF: {}'
            logger.info(message.format(self.path))
            self.count = None
            return
        try:
            reader = PDFReader(cutter.path, self.count)
            reader.read()
        except (TypeError, KeyError):
            message = 'PDF parser - Failed to parse PDF: {}'
            logger.info(message.format(self.path))
            self.count = None
            return
        if not self.path == cutter.path:
            self._remove(cutter.path)
        self.count = cutter.original
        self.year = self._year(reader.text)


class BaseSpider(Spider):

    # static methods

    @staticmethod
    def _data(settings):
        '''Return matrix from CSV file.'''
        input_dir = settings.get('INPUT_DIR')
        input_file = settings.get('INPUT_FILE')
        if not input_dir:
            raise NotConfigured('Input directory not specified.')
        if not input_file:
            raise NotConfigured('Input file not specified.')
        message = 'Base spider - Starting crawl for file: {}'
        logger.info(message.format(input_file))
        fname = os.path.join(input_dir, input_file)
        try:
            with open(fname, 'r', encoding='utf-8-sig') as file_:
                reader = csv.DictReader(file_)
                return list(reader)
        except IOError:
            raise NotConfigured('Error reading input data.')

    # private methods

    def _meta(self, row):
        '''Return request meta dictionary.'''
        return {
            'state': row.get('state'),
            'system': row.get('system'),
            'report_type': row.get('report_type')
        }

    def _process_meta(self, item, meta):
        '''Merge meta dict with item.'''
        item['state'] = meta['state']
        item['system'] = meta['system']
        item['report_type'] = meta['report_type']
        return item


class SearchSpider(BaseSpider):

    # private methods

    def _query(self, row):
        '''Return search query.'''
        site = row.get('site')
        if site:
            extract = tldextract.extract(site)
            site = 'site:{}.{}'.format(extract.domain, extract.suffix)
        query = [row.get('keyword'), row.get('modifier'), site, 'filetype:pdf']
        return ' '.join([i for i in query if i])


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
            logger.info('Custom settings - PDF Download disabled.')
            return {
                'pension_crawler.pipelines.CSVPipeline': 300,
            }
        logger.info('Custom settings - PDF Download enabled.')
        return {
            'scrapy.pipelines.files.FilesPipeline': 1,
            'pension_crawler.pipelines.PDFPipeline': 300,
            'pension_crawler.pipelines.CSVPipeline': 310
        }

    @property
    def fields_to_export(self):
        '''Return fields to export'''
        if not self.download_enabled:
            for key in ['year', 'page_count', 'path']:
                if key in self.fields:
                    self.fields.remove(key)
        return self.fields
