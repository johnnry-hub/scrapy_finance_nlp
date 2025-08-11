import scrapy
from bs4 import BeautifulSoup
from datetime import datetime
from financeSpider.items import FinancespiderItem
import time
import re
import json
#爬取新浪财经的滚动新闻，当前页面跟页面源代码不一样，通过开发者工具F12翻页分析有api接口数据，所以通过api解析link和title     scrapy crawl sina_finance

class SinaFinanceSpider(scrapy.Spider):
    name = "sina_finance"
    allowed_domains = ["sina.com.cn"]
    start_urls = ["https://finance.sina.com.cn/roll"]

    def start_requests(self):
        # 动态生成时间戳
        timestamp = int(time.time() * 1000)
        # 构造URL（不带callback）
        for i in range(1,36):
        # 想要一天的新闻数据，查了估计要35页
            time.sleep(0.5)
            url = f"https://feed.mix.sina.com.cn/api/roll/get?pageid=384&lid=2519&num=50&page={i}&_={timestamp}"
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self, response):
        data = json.loads(response.text)  # 处理JSONP响应
        # print(data)

        # with open("data.json", "w", encoding="utf-8") as f:
        #     json.dump(data, f, ensure_ascii=False, indent=4)

        for d in data['result']['data']:
            # 初始化
            finance_item = FinancespiderItem()
            finance_item['title'] = d['title'].strip()
            finance_item['link'] = d['url']
            finance_item['source'] = '新浪财经'
            finance_item['source_url'] = response.url
            # print (finance_item['source_url']+"\t"+ finance_item['link'])
            time.sleep(0.5)
            yield scrapy.Request(url=finance_item['link'], meta={"finance_item": finance_item}, callback=self.parse1)

    def parse1(self, response):

        finance_item = response.meta['finance_item']
        soup = BeautifulSoup(response.text, 'lxml')
        print("正在抓取内容")

        content="none"
        dt="none"
        source="none"
        # 元素解析异常处理
        try:
            content = soup.find("div", class_="article").text.strip()
            # finance_item["content"] = soup.select_one('div[id*="ContentBody"]').text.strip()
            dt = soup.find("span", class_="date").text.strip()
            source = soup.select_one('[class*="source ent-source"]').text.strip()

        except AttributeError as e:
            print(f"{e}:文本解析报错")

        # 去掉无用内容
        pattern = r'(' \
                  r'风险提示：[^。；\n]*[。；\n]*|' \
                  r'来源：[^。；\n]*[。；\n]*|' \
                  r'海量资讯、精准解读，尽在新浪财经APP[.*]*|' \
                  r'责任编辑：[^。；\n]*[。；\n]*|' \
                  r'新浪声明：[^。；\n]*[。；\n]*|' \
                  r'[（]总台记者[\s：]+[^。；\n]*|' \
                  r')'
        finance_item["content"]=re.sub(pattern,"",content)
        # 时间格式转换
        finance_item["update_time"] = re.sub(r"(\d+)年(\d+)月(\d+)日", r"\1-\2-\3", dt)
        finance_item['news_source'] = source
        # time.sleep(0.5)
        # print (finance_item)

        yield finance_item