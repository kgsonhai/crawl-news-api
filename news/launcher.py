import datetime

from scrapy.spiderloader import SpiderLoader
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from news.spiders.base import BaseSpider


def run_spider(spider_name: str, **kwargs):
    project_settings = get_project_settings()
    spider_loader = SpiderLoader(project_settings)
    spider_cls = spider_loader.load(spider_name=spider_name)
    if not issubclass(spider_cls, BaseSpider):
        raise ValueError(f"Spider {spider_cls.name} must inherit from class {BaseSpider.name}")
    # Init and run process crawler
    process = CrawlerProcess(settings=project_settings)
    process.crawl(crawler_or_spidercls=spider_cls, **kwargs)
    process.start()


def run_all_spider():
    project_settings = get_project_settings()
    spider_loader = SpiderLoader(project_settings)
    spider_names = spider_loader.list()
    spider_names.remove(BaseSpider.name)
    # Init and run process crawler
    process = CrawlerProcess(settings=project_settings)
    for name in spider_names:
        spider_cls = spider_loader.load(spider_name=name)
        if not issubclass(spider_cls, BaseSpider):
            raise ValueError(f"Spider {spider_cls.name} must inherit from class {BaseSpider.name}")
        process.crawl(crawler_or_spidercls=spider_cls)
    process.start(stop_after_crawl=True)
    process.join()


# def run():
if __name__ == "__main__":
    # run_spider(spider_name="dantri")
    run_all_spider()
    print('Crawl complete')
