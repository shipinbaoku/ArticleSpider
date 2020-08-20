# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline

from utils.common import json_serial


class ArticlespiderPipeline:
    def process_item(self, item, spider):
        return item


# 重写scrapy.pipelines.images.ImagesPipeline 获取图片下载地址 给items

class ArticleImagesPipeline(ImagesPipeline):

    def item_completed(self, results, item, info):
        image_file_path = ""
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item


class JsonWithEncodingPipeline:
    """
    自定义导出到json文件
    """

    def __init__(self):
        # 以a追加，以w方式打开会覆盖
        self.file = codecs.open('article.json', 'a', encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False, default=json_serial) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MysqlPipeline(object):

    def process_item(self, item, spider):
        """
        每个item中都实现save_into_sql()方法，就可以用同一个MysqlPipeline去处理
        :param item:
        :param spider:
        :return:
        """
        item.save_into_sql()
        return item
        # if CnblogsArticle.table_exists() == False:
        #     CnblogsArticle.create_table()
        # try:
        #     data = CnblogsArticle.get(CnblogsArticle.url_object_id == item["url_object_id"])
        #     data.title = item["title"]
        #     data.content = item["content"]
        #     data.url = item["url"]
        #     data.url_object_id = item["url_object_id"]
        #     data.comment_nums = item["comment_nums"]
        #     data.create_date = item["create_date"]
        #     data.fav_nums = item["fav_nums"]
        #     data.front_image_path = item["front_image_path"]
        #     data.front_image_url = item["front_image_url"]
        #     data.parise_nums = item["parise_nums"]
        #     data.tags = item["tags"]
        #     # data.save()
        # except:
        #     data = CnblogsArticle()
        #     data.title = item["title"]
        #     data.content = item["content"]
        #     data.url = item["url"]
        #     data.url_object_id = item["url_object_id"]
        #     data.comment_nums = item["comment_nums"]
        #     data.create_date = item["create_date"]
        #     data.fav_nums = item["fav_nums"]
        #     data.front_image_path = item["front_image_path"]
        #     data.front_image_url = item["front_image_url"]
        #     data.parise_nums = item["parise_nums"]
        #     data.tags = item["tags"]
        # data.save()
        # return item
