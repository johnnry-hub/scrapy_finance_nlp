import scrapy
import time
from bs4 import BeautifulSoup
from financeSpider.items import FinancespiderItem

# 爬取财联社的头条新闻,模拟人类点击加载更多 https://www.cls.cn/depth?id=1000  使用selenium + Beautifulsoup技术  scrapy crawl cls_finance

class ClsFinanceSpider(scrapy.Spider):
    name = "cls_finance"
    allowed_domains = ["cls.cn"]
    start_urls = ["https://www.cls.cn/"]

    #因为要使用selenium重写请求首页
    def start_requests(self):
        url="https://www.cls.cn/depth?id=1000"
        yield scrapy.Request(url=url,meta={"use_selenium":True},callback=self.parse) # 标记需要处理 只有需要selenium的时候标记，默认不用

    def parse(self, response):

        soup = BeautifulSoup(response.text, 'lxml')
        # print (soup)
        # 用css模糊匹配
        items = soup.select('div[class*="subject-interest-list"]')
        # print (items)
        for t in items:
            item = FinancespiderItem()
            item['source'] = '财联社'
            item['source_url'] = response.url
            item['title'] = t.select_one('div[class*="subject-interest-title"]').text.replace('原创', '').strip()
            item['link'] = "https://www.cls.cn" + t.a['href']
            # print(item['link'] )
            # print (item['title'])
            time.sleep(0.5)
            yield scrapy.Request(url=item['link'], meta={"item": item}, callback=self.parse1)

    def parse1(self, response):
        item = response.meta['item']
        soup = BeautifulSoup(response.text, 'lxml')
        print("正在抓取内容")

        # 声明变量并赋值，这样能在解析异常的时候还能正常入表
        content = "none"
        dt = "none"
        source = "none"
        # 文本解析异常处理
        try:
            content = soup.select_one('div[class*="detail-content"]').text.strip()
            dt = soup.select_one('div[class="f-l m-r-10"]').text.strip()[0:16]
            source = soup.select_one('div[class="f-l"]').text.strip()

        except AttributeError as e:
            print (f"{e}:文本解析报错")

        item["content"] = content
        item['update_time']=dt
        item['news_source'] =source
        time.sleep(0.5)
        #
        # print  (item["content"] +"\t"+item['update_time'])
        yield item


