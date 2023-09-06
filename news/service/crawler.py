import json
from datetime import datetime
from multiprocessing.context import Process

import requests

from news.launcher import run_all_spider, run_spider
from news.model.newscrawler import NewsCrawler
from news.settings import UPDATE_NEWS_CRAWLER_STATUS_API_URL


class CrawlerService:

    @staticmethod
    def run_crawler(news_crawler: NewsCrawler):
        try:
            # process = Process(target=run_spider, args=("vnexpress",))
            process = Process(target=run_all_spider)
            process.start()
            process.join()
            process.terminate()
            print('Crawl complete')
            data = NewsCrawler(session_id=news_crawler.session_id, status='NEWS_CRAWLER_SUCCESS')
            json_data = data.__dict__
            requests.post(url=UPDATE_NEWS_CRAWLER_STATUS_API_URL, json=json_data)
        except(Exception,) as ex:
            data = NewsCrawler(session_id=news_crawler.session_id, status='NEWS_CRAWLER_FAILED')
            json_data = data.__dict__
            requests.post(url=UPDATE_NEWS_CRAWLER_STATUS_API_URL, json=json_data)
            print(f'Error run spider: {ex}')


if __name__ == '__main__':
    data1 = NewsCrawler(session_id=9, status='NEWS_CRAWLER_SUCCESS')
    json_data1 = data1.__dict__
    print(json_data1)
    requests.post(url=UPDATE_NEWS_CRAWLER_STATUS_API_URL, json=json_data1)
