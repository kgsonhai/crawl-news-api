import datetime
import re

from scrapy import Spider


def parse_datetime(datetime_str):
    try:
        date_pattern = re.compile(r"\d{1,2}[\/|-]\d{1,2}[\/|-]\d{4}")
        time_pattern = re.compile(r"\d{1,2}:\d{1,2}")

        date_str = re.findall(date_pattern, datetime_str)
        if len(date_str) == 1:
            date_str = date_str[0]
        else:
            raise Exception(f"Cannot parser date from {datetime_str}")

        time_str = re.findall(time_pattern, datetime_str)
        if len(time_str) == 1:
            time_str = time_str[0]
        else:
            raise Exception(f"Cannot parser time from {datetime_str}")
    except(Exception,) as exc:
        return datetime.datetime.now()

    datetime_str = date_str + " " + time_str
    datetime_str = datetime_str.replace('-', '/')
    return datetime.datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')


def check_valid_text(text):
    if text is None:
        return False
    if re.findall(r"\w", text):
        return True
    return False


class BaseSpider(Spider):
    name = 'base-spider'
    id_spider = None

    def start_requests(self):
        raise NotImplementedError

    def parse(self, response, **kwargs):
        raise NotImplementedError
