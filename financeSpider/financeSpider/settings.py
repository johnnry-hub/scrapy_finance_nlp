# Scrapy settings for financeSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "financeSpider"

SPIDER_MODULES = ["financeSpider.spiders"]
NEWSPIDER_MODULE = "financeSpider.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
RETRY_HTTP_CODES = [401, 403, 500, 502, 503, 504]
CONCURRENT_REQUESTS = 10

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED =True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'connection': 'keep-alive',
    'cookie':'qgqp_b_id=c1797999ea697cca0b8cdb301946154d; fullscreengg=1; fullscreengg2=1; st_si=08362192258136; st_asi=delete; st_pvi=17251250121320; st_sp=2025-05-11%2016%3A41%3A43; st_inirUrl=https%3A%2F%2Ffinance.eastmoney.com%2Fa%2Fccjdd_4.html; st_sn=43; st_psi=20250511235833627-113104312931-9957797338',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}



# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "financeSpider.middlewares.FinancespiderSpiderMiddleware": 543,
#}
# 禁用Scrapy内置的重定向中间件
# REDIRECT_ENABLED = False
# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

#下载中间件
DOWNLOADER_MIDDLEWARES = {
   "financeSpider.middlewares.FinancespiderSpiderMiddleware": 543,
   "financeSpider.middlewares.SeleniumMiddleware": 600

}



# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}
# mysql SETTING========mysql数据库配置
MYSQL_HOST='XXX.XXX.XX.XXX'
MYSQL_PORT=3306
MYSQL_USER='root'
MYSQL_PASSWORD='XXX'
MYSQL_DATABASE = 'finance'
MYSQL_CHARSET='utf8mb4'

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # "financeSpider.pipelines.FinanceSpiderPipeline": 300,
    #存储在csv文件
    "financeSpider.pipelines.FinanceCsvPipeline": 300,
    #存储在mysql数据库
    # "financeSpider.pipelines.MySQLPipeline": 300,

}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
# REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"




