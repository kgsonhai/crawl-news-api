from pymongo import MongoClient
from news.settings import MONGO_URI, MONGO_DATABASE, MONGO_COLLECTION


class MongoDB:
    myclient = MongoClient(MONGO_URI)
    mydb = myclient[MONGO_DATABASE]
    mycol = mydb[MONGO_COLLECTION]

    def get_articles_by_url(self, url: str):
        query = {"url": {"$regex": url}}
        return self.mycol.find_one(query)


if __name__ == '__main__':
    data = MongoDB().get_articles_by_url(url="282110")
    if data is not None:
        print(data)
