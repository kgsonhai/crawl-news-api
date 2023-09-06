import uuid

import scrapy
from scrapy.http.response import Response

from .base import BaseSpider, parse_datetime, check_valid_text
from ..data.mongo import MongoDB


class VnexpressSpider(BaseSpider):
    name = 'vnexpress'
    mongo = MongoDB()

    def start_requests(self):
        urls_dict = {
            "https://vnexpress.net/thoi-su/chinh-tri": "chinh-tri",
            "https://vnexpress.net/doi-song": "xa-hoi",
            "https://vnexpress.net/kinh-doanh": "kinh-te",
            "https://vnexpress.net/giao-duc": "giao-duc",
            "https://vnexpress.net/khoa-hoc/tin-tuc": "khoa-hoc",
            "https://vnexpress.net/suc-khoe/tin-tuc": "y-te",
            "https://vnexpress.net/the-thao": "the-thao",
            "https://vnexpress.net/giai-tri": "giai-tri"
        }
        for url in urls_dict:
            yield scrapy.Request(url=url, callback=self.parse_article_url_list, meta={"category_url": url,
                                                                                      "category": urls_dict[url]})

    def parse_article_url_list(self, response):
        urls = response.css('html').re(r'https:\/\/vnexpress.*-\d{7}.html')
        urls = list(set(urls))

        for url in urls:
            if self.mongo.get_articles_by_url(url) is None:
                meta = response.meta
                meta['url'] = url
                yield scrapy.Request(url=url, callback=self.parse_content_article, meta=meta)

    def parse_content_article(self, response: Response): 
        image_urls = response.xpath('//div[contains(@class, "fig-picture")]//img/@data-src').get() or response.xpath('//div[contains(@class, "block_thumb_picture")]//img/@data-src').get()
        title = response.css('h1.title-detail::text').get()
        title = title if title is not None else response.css('h1.title-detail b::text').get()
        content = ""

        for node in response.xpath('//p[@class="Normal"]'):
            content = content + node.xpath('string()').extract()[0] + " "
        if check_valid_text(title) is False or check_valid_text(content) is False:
            yield {}
            print('yeild')
        else:
            article = {
                'uuid': str(uuid.uuid5(uuid.NAMESPACE_DNS, response.url)),
                'url': response.meta['url'],
                'domain': self.name,
                'title': title.strip(),
                'category_url': response.meta['category_url'],
                'category': response.meta['category'],
                'time': parse_datetime(response.css('.date::text').get()),
                'content': content.replace("Nguồn:", "").replace("(Theo  )", "").strip(),
                'img_urls': image_urls,
            }
            yield article
