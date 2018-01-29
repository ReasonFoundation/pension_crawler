'''items.py'''

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class ResultItem(Item):

    '''Result item.'''

    total = Field()
    url = Field()
    title = Field()
    snippet = Field()
    timestamp = Field()


class ResultItemLoader(ItemLoader):

    '''Result item loader.'''

    default_item_class = ResultItem
    default_output_processor = TakeFirst()
