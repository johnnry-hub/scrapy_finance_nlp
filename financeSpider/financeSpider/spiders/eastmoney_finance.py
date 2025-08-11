import scrapy
from financeSpider.items import FinancespiderItem
import json
import random
import time
import re
from bs4 import BeautifulSoup


# 爬取东方福利网财经导读https://finance.eastmoney.com/a/ccjdd.html前10页新闻，因为是动态渲染页面，通过开发者工具F12分析选用更为高效的接口api解析
# scrapy genspider eastmoney_finance np-listapi.eastmoney.com          scrapy crawl eastmoney_finance

class EastmoneyFinanceSpider(scrapy.Spider):
    name = "eastmoney_finance"
    allowed_domains = ["eastmoney.com"]
    start_urls = ["https://np-listapi.eastmoney.com"]

    def start_requests(self):

        for page in range(1, 11):
            item = FinancespiderItem()
            # 动态参数生态jQuery
            random_str = '1' + ''.join(str(random.randint(0, 9)) for _ in range(19))
            callback = f"jQuery{random_str}_{str(int(time.time() * 1000))}"
            timestamp = str(int(time.time() * 1000))
            item['source'] = '东方财富网'
            item['source_url'] = f"https://finance.eastmoney.com/a/ccjdd_{page}.html"
            # 构造url
            api_url = f'https://np-listapi.eastmoney.com/comm/web/getNewsByColumns?client=web&biz=web_news_col&column=345&order=1&needInteractData=0&page_index={page}&page_size=20&req_trace={timestamp}&fields=code,showTime,title,mediaName,summary,image,url,uniqueUrl,Np_dst&types=1,20&callback={callback}&_={timestamp}'

            # print (api_url)
            time.sleep(0.5)
            yield scrapy.Request(api_url,meta={"item": item}, callback=self.parse)

    def parse(self, response):
        item = response.meta['item']
        data = json.loads(response.text[41:-1])  # 处理JSONP响应
        # # 解析示例（需根据实际数据结构调整）：
        for d in data['data']['list']:
            # 初始化
            finance_item = FinancespiderItem()
            finance_item['title'] = d['title'].strip()
            finance_item['link'] = d['uniqueUrl']
            # finance_item['link'] = d['url']
            finance_item['source'] = item['source']
            finance_item['source_url'] = item['source_url']
            # print (finance_item['source_url']+"\t"+ finance_item['link'])
            time.sleep(0.5)
            yield scrapy.Request(url=finance_item['link'], meta={"finance_item": finance_item}, callback=self.parse2)

    def parse2(self, response):
        finance_item = response.meta['finance_item']

        soup = BeautifulSoup(response.text, 'lxml')
        print("正在抓取内容")

        # 先给变量赋值以免数据丢失
        content="none"
        dt="none"
        source="none"
        # 文章元素解析异常处理
        try:
            content = soup.find("div", id="ContentBody").text.strip()
            # finance_item["content"] = soup.select_one('div[id*="ContentBody"]').text.strip()

            if 'fund.eastmoney.com' in response.url:
                dt = soup.find("div", class_=" item").text.strip()
                source= soup.find("div", class_="source").text.strip()
            else:

                dt = soup.find("div", class_="infos").text.strip()[0:17]
                source = soup.find("div", class_="infos").text.strip()[18:].replace('\n', '').replace('\r', '').replace(' ', '')

        except AttributeError as e:
            print(f"{e}:文本解析报错")

        # print (source)
        # time.sleep(0.5)
        # 去除无用信息 如（文章来源：每日经济新闻）
        finance_item["content"]=re.sub(r"[\(（]文章来源[^)）]*[\)）]", "", content)
        # 时间格式转换
        finance_item["update_time"] = re.sub(r"(\d+)年(\d+)月(\d+)日", r"\1-\2-\3", dt)
        match = re.search(r'来源：\s*(\S+)', source)
        if match:
            finance_item['news_source'] = match.group(1)
        else:
            finance_item['news_source']=source

        # print (finance_item)
        yield finance_item
