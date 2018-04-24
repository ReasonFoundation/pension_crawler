'''loaders.py'''

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity

from pension_crawler.items import ResultItem, PDFItem


class BaseLoader(ItemLoader):

    '''Base item loader.'''

    default_output_processor = TakeFirst()
    file_urls_out = Identity()


class ResultLoader(BaseLoader):

    '''Result item loader.'''

    default_item_class = ResultItem


class PDFLoader(BaseLoader):

    '''PDF item loader.'''

    default_item_class = PDFItem
