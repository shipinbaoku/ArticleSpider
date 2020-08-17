from peewee import *

database = MySQLDatabase('article_spider',
                         **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': '127.0.0.1',
                            'port': 3306, 'user': 'root', 'password': 'root'})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class CnblogsArticle(BaseModel):
    comment_nums = IntegerField(constraints=[SQL("DEFAULT 0")])
    content = TextField(null=True)
    create_date = DateTimeField(null=True)
    fav_nums = IntegerField(constraints=[SQL("DEFAULT 0")])
    front_image_path = CharField(null=True)
    front_image_url = CharField(null=True)
    parise_nums = IntegerField(constraints=[SQL("DEFAULT 0")])
    tags = CharField(null=True)
    title = CharField()
    url = CharField()
    url_object_id = CharField()

    class Meta:
        table_name = 'cnblogs_article'
