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
from scrapy import Spider
from scrapy.exceptions import NotConfigured


logger = logging.getLogger(__name__)


class PDFParser(object):

    '''Extract page count and year from PDF.'''

    # constructor

    def __init__(self, path, read_count, temp_dir):
        '''Set path and read count. Initialize reader and text to null.'''
        self.path = path
        self.original_count = read_count
        self.temp_dir = temp_dir
        self.reader = None
        self.page_count = None
        self.read_count = None
        self.year = None

    # private methods

    def _get_reader(self):
        '''Return reader object.'''
        with open(self.path, 'rb') as file_:
            return PdfFileReader(file_)

    def _get_read_count(self):
        '''Return page count if greater than read count else read count.'''
        if self.page_count >= self.original_count:
            return self.original_count
        return self.page_count

    def _write_pdf(self):
        '''Cut PDF file to read count pages and write to temporary file.'''
        writer = PdfFileWriter()
        for i in self.read_count:
            writer.addPage(self.reader.getPage(i))
        with open(self.path, 'wb') as file_:
            writer.write(file_)

    def _remove_pdf(self):
        '''Remove PDF file from temporary directory.'''
        try:
            os.remove(self.path)
        except OSError:
            pass

    def _parse_pypdf2(self):
        '''Read text from PDF file using pypdf2.'''
        text = []
        for i in range(self.read_count):
            page = self.reader.getPage(i)
            text.append(page.extractText())
        return '\n'.join(text).strip()

    def _parse_textract(self):
        '''Read text from pdf file using textract.'''
        text = textract.process(self.path, method='tesseract', language='eng')
        return text.strip()

    def _get_year(self, text):
        '''Read year from text using regex.'''
        if not text:
            return
        match = re.search(r'\b(19|20)\d{2}\b', text)
        if match:
            return match.group()

    def _mod_and_parse(self):
        '''Parse when PDF needs to be transformed.'''
        name = '{}.pdf'.format(uuid.uuid4().hex)
        self.path = os.path.join(self.temp_dir, name)
        self._write_pdf()
        self.reader = self._get_reader()
        self._remove_pdf()

    def _get_text(self):
        '''Get text using pypdf2 or textract.'''
        text = self._parse_pypdf2()
        if not text:
            text = self._parse_textract()
        return text

    # public methods

    def parse(self):
        '''Parse year from PDF file.'''
        self.reader = self._get_reader()
        self.page_count = self.reader.getNumPages()
        self.read_count = self._get_read_count()
        if self.read_count >= self.original_count:
            self._mod_and_parse()
        self.year = self._get_year(self._get_text())


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
            return {
                'pension_crawler.pipelines.CSVPipeline': 300,
            }
        return {
            'scrapy.pipelines.files.FilesPipeline': 1,
            'pension_crawler.pipelines.CSVPipeline': 300
        }

    @property
    def fields_to_export(self):
        '''Return fields to export'''
        if not self.download_enabled:
            for key in ['year', 'page_count', 'path']:
                if key in self.fields:
                    self.fields.remove(key)
        return self.fields
