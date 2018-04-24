'''items.py'''

from scrapy import Item, Field


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
