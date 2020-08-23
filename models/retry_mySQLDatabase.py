from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin
"""
既使用连接池 又使用重连
"""

class RetryMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    _instance = None

    @staticmethod
    def get_db_instance():
        if not RetryMySQLDatabase._instance:
            RetryMySQLDatabase._instance = RetryMySQLDatabase(
                'article_spider',
                **{'charset': 'utf8', 'sql_mode': 'PIPES_AS_CONCAT', 'use_unicode': True,
                   'host': '127.0.0.1', 'port': 3306, 'user': 'root', 'password': 'root'}
            )
        return RetryMySQLDatabase._instance
