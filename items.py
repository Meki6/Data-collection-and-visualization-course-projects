# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Hw2Item(scrapy.Item):
    # define the fields for your item here like:
    book = scrapy.Field()
    author = scrapy.Field()
    bookintro = scrapy.Field()
    latestchapter = scrapy.Field()
    updatetime = scrapy.Field()
    # id = scrapy.Field()###为了补上昨天宕掉的第26页###
    # pass
