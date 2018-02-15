'''items.py'''

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity


class ResultItem(Item):

    '''Result item.'''

    keyword = Field()
    total = Field()
    url = Field()
    title = Field()
    snippet = Field()
    file_urls = Field()
    files = Field()
    timestamp = Field()


class PDFItem(Item):

    '''Pdf item.'''

    url = Field()
    href = Field()
    text = Field()
    file_urls = Field()
    files = Field()
    timestamp = Field()


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
