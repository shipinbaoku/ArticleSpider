# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from itemloaders.processors import TakeFirst, Identity, Join, MapCompose
from scrapy.loader import ItemLoader

from models.models import CnblogsArticle


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


"""
重写ItemLoader完成数据处理，清洗，针对所有采集到的元素的,个体item特殊处理见front_image_url = scrapy.Field(output_processor=Identity())，
由于Scrapy下载图片或者文件，要求的是List
"""



class TakeFirstCustom(TakeFirst):
    """
    处理采集的元素不存在问题
    """
    def __call__(self, values):
        for value in values:
            if value is not None and value != '':
                return value.strip() if isinstance(value, str) else value


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirstCustom()


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

    def save_into_sql(self):
        if CnblogsArticle.table_exists() == False:
            CnblogsArticle.create_table()

        try:
            data = CnblogsArticle.get(CnblogsArticle.url_object_id == self["url_object_id"])
            data.title = self["title"]
            data.content = self["content"]
            data.url = self["url"]
            data.url_object_id = self["url_object_id"]
            data.comment_nums = self["comment_nums"]
            data.create_date = self["create_date"]
            data.fav_nums = self["fav_nums"]
            data.front_image_path = self["front_image_path"]
            data.front_image_url = self["front_image_url"]
            data.parise_nums = self["parise_nums"]
            data.tags = self["tags"]
            data.save()
        except:
            data = CnblogsArticle()
            data.title = self["title"]
            data.content = self["content"]
            data.url = self["url"]
            data.url_object_id = self["url_object_id"]
            data.comment_nums = self["comment_nums"]
            data.create_date = self["create_date"]
            data.fav_nums = self["fav_nums"]
            data.front_image_path = self["front_image_path"]
            data.front_image_url = self["front_image_url"]
            data.parise_nums = self["parise_nums"]
            data.tags = self["tags"]
            data.save()
        return self


"""
知乎相关Item
"""


class ZhihuQuestionItem(scrapy.Item):
    # 知乎的问题 item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()


class ZhihuAnswerItem(scrapy.Item):
    # 知乎的问题回答item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    parise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
