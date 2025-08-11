import scrapy
import time
from bs4 import BeautifulSoup
from financeSpider.items import FinancespiderItem

# 爬取同花顺的股票-要闻精华https://stock.10jqka.com.cn/ywjh_list/ 分析发现是静态页面         scrapy crawl ths_finance

class ThsFinanceSpider(scrapy.Spider):
    name = "ths_finance"
    allowed_domains = ["10jqka.com.cn"]
    start_urls = ["https://stock.10jqka.com.cn/ywjh_list/"]

    #需要翻页，重写start_requests
    def start_requests(self):

        # 构造URL
        for i in range(1,21):
        # 想要一天的新闻数据，查了估计要20页
            time.sleep(0.5)
            url = f"https://stock.10jqka.com.cn/ywjh_list/index_{i}.shtml"
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self, response):
        # response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        #print (soup)
        news_items =soup.find_all('span', class_='arc-title')
        # print (news_items)

        for t in news_items:
            item = FinancespiderItem()
            item['source'] = '同花顺'
            item['source_url'] = response.url
            item['title'] = t.a.text.strip()
            item['link'] = t.a['href']
            # title =item['title']
            # link = item['link']
            # print (title,link)
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
            # content = soup.select_one('div[id="contentApp"]').text.strip()
            content=soup.find("div", id="contentApp").text.strip()
            dt = soup.find("span",id="pubtime_baidu").text.strip()[:-3]
            source = soup.find("a",id="sourcename").text.strip()


        except AttributeError:
            print("AttributeError:文本解析报错")

        item["content"] = content
        item['update_time'] = dt
        item['news_source'] = source
        # time.sleep(0.5)
        # print (item)
        yield item



