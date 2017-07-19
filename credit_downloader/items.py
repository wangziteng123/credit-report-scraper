# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CreditDownloaderItem(scrapy.Item):
    id_ = scrapy.Field()
    name = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
    rating = scrapy.Field()
    pub_time = scrapy.Field()
    fet_time = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()
    status = scrapy.Field()
