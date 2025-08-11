import scrapy
import time
from bs4 import BeautifulSoup
from financeSpider.items import FinancespiderItem
import json
import re
from urllib.parse import urlparse
from datetime import datetime


# 爬取华尔街见闻的最新资讯 https://wallstreetcn.com/news/global 通过F12开发者工具的network发现有接口文件随着页面加载不断变化https://api-one-wscn.awtmt.com/apiv1/content/information-flow?channel=global&accept=article&cursor=&limit=20&action=upglide
# 然后通过分析发现把limit到100以后能显示接口的全部数据https://api-one-wscn.awtmt.com/apiv1/content/information-flow?channel=global&accept=article&limit=200
# 新闻文章内容也是通过动态渲染页面，通过api推送过来的，https://api-one-wscn.awtmt.com/apiv1/content/articles/3747700?extract=0        scrapy crawl wal_finance

class WalFinanceSpider(scrapy.Spider):
    name = "wal_finance"
    allowed_domains = ["awtmt.com"]  #domain一定要改成api接口的domain
    start_urls = ["https://api-one-wscn.awtmt.com/apiv1/content/information-flow?channel=global&accept=article&limit=200"]

    def parse(self, response):
        data = json.loads(response.text)
        # soup = BeautifulSoup(response.text, 'lxml')
        # print (data)

        data=data['data']['items']
        for d in data:
            finance_item = FinancespiderItem()
            finance_item['title']=d['resource']['title']
            finance_item['link'] = d['resource']['uri']

            url_link = urlparse(finance_item['link']).path
            match=re.search(r"/articles/\d+", url_link)
            if match:
                url_link=match.group()
            else:
                url_link = url_link

            url_api=f"https://api-one-wscn.awtmt.com/apiv1/content{url_link}?extract=1"
            finance_item['source'] = '华尔街见闻'
            finance_item['source_url'] = "https://wallstreetcn.com/news/global"
            # print (finance_item['link'],url_api)
            # print (finance_item)
            time.sleep(0.5)
            yield scrapy.Request(url_api,meta={"finance_item": finance_item}, callback=self.parse1)

    def parse1(self, response):

        finance_item = response.meta['finance_item']
        data = json.loads(response.text)
        print("正在抓取内容")
        # print(data)
        # 先赋值以防后面报错数据丢失
        finance_item['content']="none"
        finance_item['news_source']="none"
        finance_item['update_time']="none"
        # 异常处理
        try:
            content=data['data']['content']
            soup = BeautifulSoup(content, 'lxml')
            finance_item['content']=soup.text
            # print(finance_item['content'])
            finance_item['news_source']=data['data']['author']['display_name']
            dt=data['data']['display_time']
            finance_item['update_time'] =datetime.fromtimestamp(dt).strftime("%Y-%m-%d %H:%M")
        except KeyError as e:
            print(f"json解析出错：{e}")
        # print(finance_item)
        time.sleep(0.5)
        yield finance_item

