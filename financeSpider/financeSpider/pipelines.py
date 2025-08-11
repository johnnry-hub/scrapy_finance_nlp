# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter


# class FinancespiderPipeline:
#     def process_item(self, item, spider):
#         return item


import csv
from itemadapter import ItemAdapter
import datetime
import pymysql
from scrapy.exceptions import DropItem
# 获取当前日期
today = datetime.date.today()


class FinanceCsvPipeline(object):
    def process_item(self, item, spider):
        with open(f"finance_news_{today}.csv", "a+", encoding="utf-8") as f:
            w = csv.writer(f)
            row=item["link"],item["title"],item["source"],item["source_url"],item["content"],item["news_source"],item["update_time"]
            w.writerow(row)
        return item



class MySQLPipeline:
    def __init__(self, host, port, user, password, db, charset):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        self.connection = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            port=crawler.settings.get('MYSQL_PORT'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            db=crawler.settings.get('MYSQL_DATABASE'),
            charset=crawler.settings.get('MYSQL_CHARSET')
        )

    def open_spider(self, spider):
        """连接数据库"""
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        """关闭连接"""
        self.connection.close()

    def process_item(self, item, spider):
        """处理Item"""
        try:
            # 构建SQL语句（根据你的表结构修改）
            sql = """
                INSERT INTO finance_news(
                    url,
                    title,
                    source,
                    source_url,
                    content,
                    news_source,
                    update_time
                ) VALUES ( %s, %s, %s, %s, %s , %s, %s )
                ON DUPLICATE KEY UPDATE 
                title = VALUES(title), 
                source = VALUES(source),
                source_url = VALUES(source_url), 
                content = VALUES(content),
                news_source = VALUES(news_source),
                update_time = VALUES(update_time);"""
            params = (item["link"],item["title"],item["source"],item["source_url"],item["content"],item["news_source"],item["update_time"])
            # 从item提取数据（字段名需要对应）
            self.cursor.execute(sql,params)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise DropItem(f"Error saving item to MySQL: {str(e)}")
        return item

