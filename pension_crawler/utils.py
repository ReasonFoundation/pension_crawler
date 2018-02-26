'''utils.py'''


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
        if not self.download_enabled:
            self.fields.remove('path')
        return self.fields
