import uuid

import scrapy
from scrapy.http.response import Response

from .base import BaseSpider, parse_datetime, check_valid_text
from ..data.mongo import MongoDB


class VietnamnetSpider(BaseSpider):
    name = 'vietnamnet'
    mongo = MongoDB()

    def start_requests(self):
        urls_dict = {
            "https://vietnamnet.vn/thoi-su/chinh-tri": "chinh-tri",
            # "https://vietnamnet.vn/thoi-su": "xa-hoi",
            # "https://vietnamnet.vn/kinh-doanh": "kinh-te",
            # "https://vietnamnet.vn/giao-duc": "giao-duc",
            # "https://vietnamnet.vn/suc-khoe/": "y-te",
            # "https://vietnamnet.vn/thong-tin-truyen-thong/cong-nghe": "cong-nghe",
            # "https://vietnamnet.vn/the-thao": "the-thao",
            # "https://vietnamnet.vn/giai-tri": "giai-tri"
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        url_pattern = r'\/[-\w]+-\d{7}\.html'
        urls = response.css('html').re(url_pattern)
        urls = list(set(urls))
        for url in urls:
            if self.mongo.get_articles_by_url(url) is None:
                url = "https://vietnamnet.vn" + url
                meta = response.meta
                meta['url'] = url
                yield scrapy.Request(url=url, callback=self.parse_content_article,
                                     meta=meta)

    def parse_content_article(self, response: Response):
        image_urls = response.xpath('//figure[contains(@class, "vnn-content-image")]//img/@data-original').get()
        title = response.css('h1::text').get()
        content = " ".join(response.css('div.main-content p::text').getall())
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
                'time': parse_datetime(response.css('.ArticleDate::text').get()),
                'content': content.strip(),
                'img_urls': image_urls
            }
            yield article
