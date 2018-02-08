'''utils.py'''

from scrapy.exceptions import NotConfigured


class SpiderMixin(object):

    '''Common spider functionality.'''

    @staticmethod
    def parse_keywords(path):
        '''Read search keywords from input file.'''
        keywords = []
        try:
            with open(path, 'r') as file_:
                for line in file_.readlines():
                    keywords.append(line.strip().lower())
        except IOError:
            raise NotConfigured('Could not read input file.')
        if not keywords:
            raise NotConfigured('Keyword list is empty.')
        return keywords

    @staticmethod
    def parse_settings(settings):
        '''Parse common settings for all spiders.'''
        input_file = settings.get('INPUT_FILE')
        depth = settings.get('RESULT_DEPTH')
        if not input_file:
            raise NotConfigured('Input file not set.')
        return input_file, depth
