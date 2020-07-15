# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpidermusicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 歌曲id
    id = scrapy.Field()
    artist = scrapy.Field()
    album = scrapy.Field()
    music = scrapy.Field()
    comments = scrapy.Field()
