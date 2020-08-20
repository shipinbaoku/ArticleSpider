from peewee import *

database = MySQLDatabase('zhihu_question',
                         **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True, 'host': '127.0.0.1',
                            'port': 3306, 'user': 'root', 'password': 'root'})


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Answer(BaseModel):
    author_id = CharField(null=True)
    comments_num = IntegerField(constraints=[SQL("DEFAULT 0")])
    content = TextField()
    crawl_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    crawl_update_time = IntegerField(null=True)
    create_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    praise_num = IntegerField(constraints=[SQL("DEFAULT 0")])
    question_id = BigIntegerField()
    update_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    url = CharField()
    zhihu_id = BigIntegerField()

    class Meta:
        table_name = 'answer'


class Question(BaseModel):
    answer_num = IntegerField(constraints=[SQL("DEFAULT 0")])
    click_num = IntegerField(constraints=[SQL("DEFAULT 0")])
    comments_num = IntegerField(constraints=[SQL("DEFAULT 0")])
    content = TextField()
    crawl_time = IntegerField(constraints=[SQL("DEFAULT 0")])
    crawl_update_time = IntegerField(null=True)
    create_time = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    title = CharField()
    topics = CharField(null=True)
    update_time = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    url = CharField()
    watch_users_num = IntegerField(constraints=[SQL("DEFAULT 0")])
    zhihu_id = BigIntegerField()

    class Meta:
        table_name = 'question'
