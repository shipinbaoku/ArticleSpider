# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re
import time

import scrapy
from itemloaders.processors import TakeFirst, Identity, Join, MapCompose
from scrapy.loader import ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


"""
重写ItemLoader完成数据处理，清洗，针对所有采集到的元素的,个体item特殊处理见front_image_url = scrapy.Field(output_processor=Identity())，
由于Scrapy下载图片或者文件，要求的是List
"""


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def date_convert(value):
    """
    处理时间
    :param value:
    :return:
    """
    match_re = re.match(".*?(\d+.*)", value)
    if match_re:
        return match_re.group(1)
    else:
        return 0


class CnblogsArticlespiderItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(input_processor=MapCompose(date_convert))
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(output_processor=Identity())
    front_image_path = scrapy.Field()
    parise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field(output_processor=Join(separator=","))
    content = scrapy.Field()

    pass
