'''utils.py'''

import json
import logging
import os

from datetime import datetime

from scrapy.exceptions import NotConfigured


logger = logging.getLogger(__name__)


class BaseParser(object):

    '''Common arg parsing functionality.'''

    # constructor

    def __init__(self, args, settings):
        '''Set args, settings and input directory.'''
        self.args = args
        self.settings = settings
        input_dir = self._from_settings('input_dir')
        if not input_dir:
            raise NotConfigured('No input directory specified.')
        self.input_dir = input_dir

    # private methods

    def _from_args(self, key):
        '''Safe retrieve value from spider arguments.'''
        try:
            return self.args.pop(key)
        except KeyError:
            print('Key {} not found in spider arguments.'.format(key))

    def _from_settings(self, key):
        '''Safe retrieve value from spider settings.'''
        try:
            return self.settings[key]
        except KeyError:
            print('Key {} not found in spider settings.'.format(key))

    def _from_args_or_settings(self, key):
        '''Retrieve value from spider arguments or settings.'''
        return self._from_args(key) or self._from_settings(key)

    def _from_json(self, text):
        '''Load JSON from string.'''
        try:
            return json.loads(text)
        except ValueError:
            print('JSON conversion error.')
            return []

    def _from_file(self, path):
        '''Return values from file input.'''
        with open(path, 'r') as file_:
            return [i.strip() for i in file_.readlines()]


class SearchParser(BaseParser):

    '''Common arg parsing functionality for search spiders.'''

    # constructor

    def __init__(self, *args, **kwargs):
        '''Set modifier and filetype.'''
        super(SearchParser, self).__init__(*args, **kwargs)
        modifier = self._from_args_or_settings('modifier')
        filetype = self._from_args_or_settings('filetype')
        if not modifier:
            raise NotConfigured('No query modifier specified.')
        if not filetype:
            raise NotConfigured('No query filetype specified.')
        self.modifier = modifier
        self.filetype = filetype

    # private methods

    def _query(self, keyword, modifier):
        '''Return joined query.'''
        query = [keyword, modifier, 'filetype:{}'.format(self.filetype)]
        return ' '.join(query)

    def _keyword_query_list(self, lst):
        '''Return keyword query list.'''
        return [self._query(i, self.modifier) for i in lst]

    def _site_query_list(self, lst):
        '''Return site query list.'''
        return [self._query(self.modifier, i) for i in lst]

    # properties

    @property
    def api_key(self):
        '''Return API key or raise.'''
        value = self._from_settings('api_key')
        if not value:
            raise NotConfigured('API key missing.')
        return value

    @property
    def input_list(self):
        '''Return input list.'''
        keyword_list = self._from_args('keyword_list')
        if keyword_list:
            return self._keyword_query_list(self._from_json(keyword_list))
        site_list = self._from_args('site_list')
        if site_list:
            return self._site_query_list(self._from_json(site_list))
        keyword_file = self._from_args_or_settings('keyword_file')
        if keyword_file:
            return self._keyword_query_list(self._from_file(keyword_file))
        site_file = self._from_args_or_settings('site_file')
        if site_file:
            return self._site_query_list(self._from_file(site_file))
        raise NotConfigured('Input list not configured.')

    @property
    def depth(self):
        '''Return depth.'''
        return self._from_args_or_settings('depth')


class GoogleParser(SearchParser):

    '''Parse google spider arguments from call or settings.'''

    # private methods

    def _validate(self, date):
        '''Check if date is in correct format.'''
        try:
            datetime.strptime(date, '%Y%m%d')
        except ValueError:
            raise NotConfigured('Invalid date: {}.'.format(date))
        return date

    # properties

    @property
    def engine_id(self):
        '''Return API key.'''
        value = self._from_settings('engine_id')
        if not value:
            raise NotConfigured('Search engine id missing.')
        return value

    @property
    def start_date(self):
        '''Return start date'''
        return self._validate(self._from_args_or_settings('start_date'))

    @property
    def end_date(self):
        '''Return end date'''
        return self._validate(self._from_args_or_settings('end_date'))


class BingParser(SearchParser):

    '''Parse bing spider arguments from call or settings.'''

    # private methods

    def _validate(self, freshness):
        '''Check if freshness is in correct format.'''
        if freshness not in ['Day', 'Week', 'Month']:
            raise NotConfigured('Invalid freshness: {}'.format(freshness))
        return freshness

    # properties

    @property
    def freshness(self):
        '''Return freshness.'''
        return self._validate(self._from_args_or_settings('freshness'))


class SitesParser(BaseParser):

    '''Parse sites spider arguments from call or settings.'''

    # properties

    @property
    def input_list(self):
        '''Return input list.'''
        site_list = self._from_args('site_list')
        if site_list:
            return self._from_json(site_list)
        site_file = self._from_args_or_settings('site_file')
        if site_file:
            return self._from_file(site_file)
        raise NotConfigured('Input list not configured.')


class Settings(object):

    '''Return specific settings object if PDF download is enabled or not.'''

    # constructor

    def __init__(self, download):
        '''Set download.'''
        self.download = download

    # properties

    @property
    def item_pipelines(self):
        '''Return item pipelines.'''
        if not self.download:
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
        fields = ['keyword', 'url', 'title', 'path']
        if not self.download:
            fields.pop()
        return fields
