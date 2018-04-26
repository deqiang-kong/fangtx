# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi

from fangtx.items import NewHouseItem, ESFHouseItem
from fangtx.utils.connect import connect_net, create_table, dbparams


class FangtxPipeline(object):

    # 爬虫启动
    def open_spider(self, spider):
        print(spider.name + "爬虫启动.............")
        self.conn = connect_net()
        create_table()

        # 数据库连接池
        self.dbpool = adbapi.ConnectionPool('pymysql', **dbparams)
        self._sql_new = None
        self._sql_esf = None
        # 爬虫结束

    def close_spider(self, spider):
        print(spider.name + "爬虫结束.............")
        # self.conn.close()

    #
    def process_item(self, item, spider):
        # 新房存储
        if isinstance(item, NewHouseItem):
            # 异步插入
            defer = self.dbpool.runInteraction(self.insert_new_item, item)
            defer.addErrback(self.handle_error, item, spider)
            # print(item)
        # 旧房存储
        elif isinstance(item, ESFHouseItem):
            # print("xin")
            defer = self.dbpool.runInteraction(self.insert_esf_item, item)
            defer.addErrback(self.handle_error, item, spider)
        return item

    # 将方法变成属性
    @property
    def sql_new(self):
        if not self._sql_new:
            self._sql_new = """
                   insert into new_house_table(province,city,community,price,rooms,area,address,district,sale,origin_url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
            return self._sql_new
        return self._sql_new

    #
    def insert_new_item(self, cursor, item):
        cursor.execute(self.sql_new, (
            item['province'], item['city'], item['community'], item['price'], item['rooms'], item['area'],
            item['address'], item['district'], item['sale'],
            item['origin_url']))

        # 层


    @property
    def sql_esf(self):
        if not self._sql_esf:
            self._sql_esf = """
                         insert into esf_house_table(province,city,community,price,unit,floor,toward,construct,address,area,origin_url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                         """
            return self._sql_esf
        return self._sql_esf

    #
    def insert_esf_item(self, cursor, item):
        cursor.execute(self.sql_esf, (
            item['province'], item['city'], item['community'], item['price'], item['unit'],
            item['floor'],item['toward'],item['construct'],item['address'],item['area'],
            item['origin_url']))
    # 错误输出
    def handle_error(self, error, item, spider):
        print('=' * 10 + "error" + '=' * 10)
        print(error)
        print('=' * 10 + "error" + '=' * 10)
