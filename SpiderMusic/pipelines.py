# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from urllib import parse

class SpidermusicPipeline:
    def process_item(self, item, spider):
        return item

class MongoPipeline:

    collection_name = 'spider_music'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')

        )

    def open_spider(self, spider):
        user = parse.quote_plus("admin")
        passwd = parse.quote_plus("lyh@lulu520")
        self.client = pymongo.MongoClient('mongodb://{}:{}@localhost:27017/'.format(user, passwd))
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[item.table_name].update({'id': item.get('id')}, {'$set': dict(item)}, True)
        return item
