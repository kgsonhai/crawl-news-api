import uuid

import scrapy
from scrapy.http.response import Response

from .base import BaseSpider, parse_datetime, check_valid_text
from ..data.mongo import MongoDB


class NhanDanSpider(BaseSpider):
    name = 'nhandan'
    mongo = MongoDB()

    def start_requests(self):
        urls_dict = {
            "https://nhandan.vn/chinhtri/": "chinh-tri",
            "https://nhandan.vn/xahoi/": "xa-hoi",
            "https://nhandan.vn/vanhoa/": "van-hoa",
            "https://nhandan.vn/kinhte/": "kinh-te",
            "https://nhandan.vn/giaoduc/": "giao-duc",
            "https://nhandan.vn/khoahoc-congnghe/": "khoa-hoc",
            "https://nhandan.vn/y-te/": "y-te",
            "https://nhandan.vn/thethao/": "the-thao",
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        url_pattern = r'https:\/\/nhandan\.vn\/[-\w]+-post\d{6}\.html'
        urls = response.css('html').re(url_pattern)
        urls = list(set(urls))

        for url in urls:
            if self.mongo.get_articles_by_url(url) is None:
                meta = response.meta
                meta['url'] = url
                yield scrapy.Request(url=url, callback=self.parse_content_article,
                                     meta=meta)

    def parse_content_article(self, response: Response):
        image_urls = response.xpath("//table[contains(@class, 'picture')]//img/@src").get()
        title = response.css('h1::text').get()
        content = " ".join(response.css('div.article__sapo::text, div.article__body p::text').getall())

        print(f'imgs: {image_urls}')

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
                'time': parse_datetime(response.css('.article__meta .time::text').get()),
                'content': content.strip(),
                'img_urls': image_urls
            }
            yield article
