# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FinancespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    source=scrapy.Field()
    source_url= scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    content = scrapy.Field()
    news_source = scrapy.Field()
    update_time = scrapy.Field()

