import uuid
from abc import ABC
from urllib.parse import urljoin

import scrapy
from scrapy.http.response import Response

from .base import BaseSpider, parse_datetime, check_valid_text
from ..data.mongo import MongoDB


class DanTriSpider(BaseSpider):
    name = 'dantri'
    mongo = MongoDB()

    def start_requests(self):
        urls_dict = {
            "https://dantri.com.vn/xa-hoi/chinh-tri.htm": "chinh-tri",
            # "https://dantri.com.vn/xa-hoi.htm": "xa-hoi",
            # "https://dantri.com.vn/van-hoa.htm": "van-hoa",
            # "https://dantri.com.vn/kinh-doanh.htm": "kinh-te",
            # "https://dantri.com.vn/giao-duc-huong-nghiep.htm": "giao-duc",
            # "https://dantri.com.vn/suc-khoe.htm": "y-te",
            # "https://dantri.com.vn/suc-manh-so.htm": "cong-nghe",
            # "https://dantri.com.vn/the-thao.htm": "the-thao",
            # "https://dantri.com.vn/giai-tri.htm": "giai-tri"
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        url_pattern = r'\/[\w-]+\/[-\w]+-\d{17}\.htm'
        urls =  response.css('html').re(url_pattern)
        urls = list(set(urls))

        for url in urls:
            if self.mongo.get_articles_by_url(url) is None:
                url = "https://dantri.com.vn" + url
                meta = response.meta
                meta['url'] = url
                yield scrapy.Request(url=url, callback=self.parse_content_article,
                                     meta=meta)

    def parse_content_article(self, response: Response):
        image_urls = response.xpath("//div[contains(@class, 'singular-content')]//img/@data-src").get()
        title = response.css('h1::text').get()
        content = " ".join(response.css('h2.singular-sapo::text, div.singular-content p::text').getall())
        if check_valid_text(title) is False or check_valid_text(content) is False:
            yield {}
        else:
            article = {
                'uuid': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
                'url': response.meta['url'],
                'domain': self.name,
                'title': title.strip(),
                'category_url': response.meta['category_url'],
                'category': response.meta['category'],
                'time': parse_datetime(response.css('.dt-news__time::text').get()),
                'content': content.strip(),
                'img_urls': image_urls
            }
            yield article
