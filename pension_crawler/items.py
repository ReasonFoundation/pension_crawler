'''items.py'''

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Identity


class BaseItem(Item):

    '''Base item.'''

    state = Field()
    system = Field()
    report_type = Field()
    year = Field()
    page_count = Field()
    file_urls = Field()
    files = Field()
    timestamp = Field()


class ResultItem(BaseItem):

    '''Result item.'''

    keyword = Field()
    total = Field()
    url = Field()
    title = Field()
    snippet = Field()


class PDFItem(BaseItem):

    '''Pdf item.'''

    url = Field()
    href = Field()
    text = Field()


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
