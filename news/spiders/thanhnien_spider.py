import uuid

import scrapy
from scrapy.http.response import Response
from w3lib.html import remove_tags, remove_tags_with_content

from .base import BaseSpider, parse_datetime, check_valid_text
from ..data.mongo import MongoDB


class ThanhNienSpider(BaseSpider):
    name = 'thanhnien'
    mongo = MongoDB()

    def start_requests(self):
        urls_dict = {
            "https://thanhnien.vn/thoi-su/chinh-tri.htm": "chinh-tri",
            "https://thanhnien.vn/doi-song.htm": "xa-hoi",
            "https://thanhnien.vn/van-hoa.htm": "van-hoa",
            "https://thanhnien.vn/kinh-te.htm": "kinh-te",
            "https://thanhnien.vn/giao-duc.htm": "giao-duc",
            "https://thanhnien.vn/suc-khoe.htm": "y-te",
            "https://thanhnien.vn/cong-nghe-game.htm": "cong-nghe",
            "https://thanhnien.vn/the-thao.htm": "the-thao",
            "https://thanhnien.vn/giai-tri.html": "giai-tri"
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        url_pattern = r'\/[-\w]+-\d{18}\.htm'
        urls = response.css('html').re(url_pattern)
        urls = list(set(urls))
        for url in urls:
            if self.mongo.get_articles_by_url(url) is None:
                url = "https://thanhnien.vn" + url
                meta = response.meta
                meta['url'] = url
                yield scrapy.Request(url=url, callback=self.parse_content_article,
                                     meta=meta)

    def parse_content_article(self, response: Response):
        image_urls = response.xpath("//div[contains(@class, 'detail-cmain')]//img/@src").get()
        title = response.css('h1.detail-title span[data-role="title"]::text').get()
        all_content = response.css('h2.detail-sapo::text, div.detail-cmain p::text, div.detail-cmain a::text').getall()
        content = ' '.join(all_content)
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
                'time': parse_datetime(response.css('time::text').get()),
                'content': content.strip(),
                'img_urls': image_urls
            }
            yield article
