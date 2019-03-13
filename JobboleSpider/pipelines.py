# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from twisted.enterprise import adbapi


# insert records into mysql asynchronously
class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            port = 8889,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # do insertion process
        query = self.dbpool.runInteraction(self.do_insert, item)
        # handle exception
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # print failure for debug
        print(failure)

    def do_insert(self, cursor, item):
        # execute insertion
        # do different insertion with different items
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)