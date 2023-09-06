# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.crawler import Crawler, Spider
from pymongo import MongoClient


class MongoDB:
    client = None
    db = None

    def __init__(self, uri, db_name, collection_name, chunk: int = 10):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.items = []
        self.chunk = chunk

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        uri = crawler.settings.get('MONGO_URI')
        db_name = crawler.settings.get('MONGO_DATABASE')
        collection_name = crawler.settings.get('MONGO_COLLECTION')
        return cls(uri, db_name, collection_name)

    def open_spider(self, spider: Spider):
        spider.logger.info('Connecting to MongoDB.....')
        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]

    def close_spider(self, spider: Spider):
        if bool(self.items):
            self.db[self.collection_name].insert_many(self.items)
            self.items = []

        spider.logger.info('Closing MongoDB.....')
        assert isinstance(self.client, MongoClient)
        self.client.close()

    def process_item(self, item: dict, spider: Spider):
        if bool(item):
            print(item)
            self.items.append(item)
        if len(self.items) >= self.chunk:
            spider.logger.info("Inserting MongoDB...")
            self.db[self.collection_name].insert_many(self.items)
            self.items = []
