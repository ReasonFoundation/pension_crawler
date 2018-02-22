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
            raise NotConfigured('Invalid JSON: {}.'.format(text))

    def _from_file(self, path):
        '''Return values from file input.'''
        with open(path, 'r') as file_:
            return [i.strip() for i in file_.readlines()]

    def _required(self, human, value):
        '''Raise not configured if value is null.'''
        if not value:
            raise NotConfigured('{} not found.'.format(human))
        return value

    @property
    def input_dir(self):
        '''Return input directory.'''
        return self._required(
            'Input directory', self._from_settings('INPUT_DIR')
        )


class SearchParser(BaseParser):

    '''Common arg parsing functionality for search spiders.'''

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
        return [self._query(self.modifier, 'site:{}'.format(i)) for i in lst]

    def _validate_depth(self, value):
        '''Check if depth is between 0 and 9.'''
        if 0 <= value <= 9:
            return value
        raise NotConfigured('Invalid depth: {}.'.format(value))

    # properties

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
            return self._required(
                'Input list', self._site_query_list(self._from_file(site_file))
            )

    @property
    def api_key(self):
        '''Return API key or raise.'''
        return self._required('API key', self._from_settings('API_KEY'))

    @property
    def depth(self):
        '''Return depth.'''
        return self._validate_depth(
            self._required('Depth', self._from_args_or_settings('depth'))
        )

    @property
    def modifier(self):
        '''Return modifier.'''
        return self._required(
            'Modifier', self._from_args_or_settings('modifier')
        )

    @property
    def filetype(self):
        '''Return filetype.'''
        return self._required(
            'Filetype', self._from_args_or_settings('filetype')
        )


class GoogleParser(SearchParser):

    '''Parse google spider arguments from call or settings.'''

    # private methods

    def _validate_date(self, text):
        '''Check if date is in correct format.'''
        try:
            datetime.strptime(text, '%Y%m%d')
        except ValueError:
            raise NotConfigured('Invalid date: {}.'.format(text))
        return text

    # properties

    @property
    def engine_id(self):
        '''Return API key.'''
        return self._required(
            'Engine ID', self._from_settings('SEARCH_ENGINE_ID')
        )

    @property
    def start_date(self):
        '''Return start date'''
        return self._validate_date(self._from_args_or_settings('start_date'))

    @property
    def end_date(self):
        '''Return end date'''
        return self._validate_date(self._from_args_or_settings('end_date'))


class BingParser(SearchParser):

    '''Parse bing spider arguments from call or settings.'''

    # private methods

    def _validate_freshness(self, text):
        '''Check if freshness is in correct format.'''
        if text not in ['Day', 'Week', 'Month']:
            raise NotConfigured('Invalid freshness: {}'.format(text))
        return text

    # properties

    @property
    def freshness(self):
        '''Return freshness.'''
        return self._validate_freshness(
            self._from_args_or_settings('freshness')
        )


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
            return self._required('Input list', self._from_file(site_file))


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
