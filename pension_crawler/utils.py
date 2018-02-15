'''utils.py'''

import json
import logging

from scrapy.exceptions import NotConfigured


logger = logging.getLogger(__name__)


def get_download_settings(download):
    '''Return search settings depending on whether download is enabled.'''
    item_pipelines = {
        'scrapy.pipelines.files.FilesPipeline': 1,
        'pension_crawler.pipelines.SearchExportDownloadEnabledPipeline': 300
    }
    fields_to_export = ['keyword', 'url', 'title', 'path']
    if not download:
        item_pipelines = {
            'pension_crawler.pipelines.SearchExportDownloadDisabledPipeline':
                300
        }
        fields_to_export = ['keyword', 'url', 'title']
    return item_pipelines, fields_to_export


class SpiderMixin(object):

    '''Common spider functionality.'''

    @staticmethod
    def get_list_from_file(settings):
        '''Return values from file input.'''
        input_file = settings.get('INPUT_FILE')
        with open(input_file, 'r') as file_:
            return [i.strip() for i in file_.readlines()]

    @staticmethod
    def get_list_from_args(args):
        '''Return values from spider arguments.'''
        keywords = args.pop('keywords')
        if not keywords:
            return
        try:
            return json.loads(keywords)
        except ValueError:
            raise NotConfigured('Keywords list from args is invalid.')

    @staticmethod
    def get_keywords(args, settings):
        keywords = SpiderMixin.get_list_from_args(args)
        if not keywords:
            logger.info('Keyword list from args is empty.')
            keywords = SpiderMixin.get_list_from_file(settings)
        if not keywords:
            raise NotConfigured('Keyword list from file is empty.')
        return keywords

    @staticmethod
    def parse_common_settings(args, settings):
        '''Parse common settings for all spiders.'''
        keywords = SpiderMixin.get_keywords(args, settings)
        depth = settings.get('RESULT_DEPTH')
        modifier = settings.get('KEYWORD_MODIFIER')
        return keywords, depth, modifier

    def get_query(self, query):
        '''Return search query.'''
        modifier = 'filetype:pdf'
        if self.modifier:
            modifier = '{} {}'.format(self.modifier, modifier)
        return '{} {}'.format(query, modifier)
