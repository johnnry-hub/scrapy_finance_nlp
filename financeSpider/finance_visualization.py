import pandas as pd
import re
import datetime
from datetime import timedelta
import jieba
import jieba.posseg as psg
from collections import Counter
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from wordcloud import WordCloud
import jieba.analyse
# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号


# 提取今天你的日期
today = datetime.date.today()
# 文件名称 自动生成今天的文件
file=f'finance_news_{today}.csv'
# 添加分词词典 把分词分的不对的词语都可以加在这里面
jieba.load_userdict('add_word.txt')
# 临时添加（最好把词添加在add_word.txt）
# 这个数据来自财联社的电报新闻，jieba分词没有把财联社正确分词，所以把财联社添加进词典
jieba.add_word("财联社")
# 读取停用词 屏蔽不需要用的词
with open('stopwords.txt','r',encoding="utf-8") as f:
    stopwords =set(f.read().split())
# 优化 用set把数据转换成无序的集合 能提高数据的运行速度
# 手动添加停用词#临时添加
stopwords=stopwords.union({'销售','人士','部门','月份','指标','旗下','环节','责任','权益','事项','观点','关系','流动性','前景','销量','金额','格局','调研','大会','原因','挑战','核心','因素','机会','主体'
                              ,'业绩','股价','单位','体验','股份有限公司','措施','行情','精准','团队','论坛','社会','股票','世界','时讯','设施','机构','板块','媒体','社交'
                              ,'建议','竞争力','代表','背景','年度','结构','时代','意见','方案','空间','阶段','渠道','变化','压力','方向','趋势','综合','数量','功能','比例'
                              ,'设计','效率','基础','协议','驱动','助力','预测','内容','策略','专业','协同','改革','股东','整体','方式','深度','重点','融合','区域','布局',
                           '关键','机制','活动','优化','突破','中心','价值','经营','水平','研究','利率','优势','监管','模式','运营','调整','股权','用户','美元','升级','生产',
                           '体系','场景','客户','成本','报告','战略','工作','系统','分析','信息','情况','分析','投资者','财联社','地区','上市','能力','用户','改革','中心','协同',
                           '金融','服务','目标','品牌','指数','资金','标准','资产','技术','国际','价格','规模','计划','建设','集团','风险','预期','收益率','','公司','中国','市场',
                           '企业','投资','发展','产品','行业','数据','全球','业务','交易','来源','时间','文章','公告','股份','管理','经济','产业','日讯','合作','影响','新闻',
                           '项目','预计','有限公司','国家','领域','平台','责任编辑','全国','资本','编辑','程度','流向','商业','总台','快讯','超过','股票指数','财讯','持股'
                             ,'研报','热门' ,'奋进','报道','总统','评估','声明','转自','成交额','前值','自选股','客户端','数据中心','栏目','基点','模拟','网讯','累计','竞价'
                              ,'个股','A股','营业收入','营收 ','基金','日报','读懂','改变','新浪','证券日报','专题','财经','股本','现报','结论','科技','政策','热点','发布公告','涨幅','净利润','合计'})

# 数据预处理+清洗
def preprocess_text(csvfile):
    # dropna删除缺失值
    # 数据集自己准备 ***文件路径自己改一下哈  注意下路径是 //
    df =pd.read_csv(csvfile).dropna()
    # drop_duplicates去除重复行
    df= df.drop_duplicates()
    # 字段名称列表
    headers = ['url','title','source','source_url','content', 'news_source','update_time']
    # 为数据添加字段名称
    df.columns = headers
    # 提取需要的字段 url,title,content,source,update_time
    df = df[['url', 'title','content','source', 'update_time']]  # 双括号创建列名的列表
    # 对网站做个筛选    '财联社|同花顺|华尔街见闻|新浪财经|东方财富网'
    # df=df[df['source'].str.contains('财联社|华尔街见闻|东方财富网', na=False)]
    # 把none值的数据删除
    df = df[df['content'] != 'none'].copy()  # 使用copy避免SettingWithCopyWarning
    # 按titil去重使用groupby方法保留最新记录
    # 找到每个title组中update_time最大的索引
    idx = df.groupby('title')['update_time'].idxmax()
    # 通过这些索引获取对应的行
    df = df.loc[idx].copy()
    # 重置索引
    df = df.reset_index(drop=True)
    # 只提取24小时内的财经新闻(已注释掉逻辑，需要用可以放开)
    now = datetime.datetime.now()
    hour24 = now - timedelta(days=1)
    df = df[df['update_time'] > hour24.strftime('%Y-%m-%d %H:%M')].copy()  # 格式化为年-月-日 时:分
    # 去除特殊符号
    pattern = re.compile('[^\u4e00-\u9fa5a-zA-Z0-9]')
    df['text'] = df['content'].apply(lambda x: re.sub(pattern, " ", x))

    return df

df = preprocess_text(file)
df.info()

# 词频
count={}
flag=('n','vn','nr','nt') #'ns',
for idx,line in df.iterrows():
    word_psg=psg.cut(line['text'])
    for word_flag in word_psg:
        word=word_flag.word
        if word_flag.flag in flag and len(word)>1 and word not in stopwords:
            count[word]=count.get(word,0)+1
# 使用元组排序：值降序(-x[1])，键升序(x[0])
sorted_items = sorted(
        count.items(),
        key=lambda x: (-x[1], x[0])
    )
# 词频排序显示
print (f'财经新闻词频前100：{sorted_items[0:100]}')

# 词频可视化
# 词频统计通过单词计数获取
# top20
ylist =sorted(count,key=count.get,reverse=True)[:20]
xlist =[count.get(word) for word in ylist]
# 设置全局字体为支持中文的字体，这里以微软雅黑为例
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 或者你系统中的其他中文字体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
plt.barh(ylist,xlist)
plt.gca().invert_yaxis()  # 反转 y轴
plt.title('财经新闻热点（出现次数多）排名', fontsize=16)

# 词云
# 用Counter方法统计词频，结果是个词典
# 3. 加载中国地图遮罩
mask = np.array(Image.open(r'china_mask.png'))  # 替换为你的图片路径
# 创建WordCloud对象
# font_path 设置字体路径

wordcloud = WordCloud(
    font_path='C:\Windows\Fonts\simhei.ttf',  # 这个是词云字体路径，字体格式一般是在电脑的这个路径下面
    background_color='white',
    # mask=mask,
    width=1200,
    height=1200,
    max_words=100
    # contour_width=0.0001,
    # contour_color="brown"

).generate_from_frequencies(count)

# # 显示词云
plt.figure(figsize=(8, 8), facecolor=None)
plt.imshow(wordcloud)
plt.axis("off")
# plt.title('财经新闻热词（出现频率高）词云', fontsize=20, pad=20)
plt.tight_layout(pad=0)
plt.show()
# 下载词云图片
wordcloud.to_file(f"finance_word_cloud_{today}.png")

# 分词关键词提取函数（去除停用词版）取前10
def extract_keywords(text, topK=10):

    words = jieba.cut(text)
    # 过滤停用词和单字词
    filtered_words = [
        word for word in words
        if word not in stopwords and len(word) > 1
    ]

    """使用TF-IDF提取关键词（基于预处理后的文本）"""
    # 预处理文本
    clean_text = " ".join(filtered_words)

    # 使用TF-IDF算法提取关键词
    keywords = jieba.analyse.extract_tags(
        clean_text,
        topK=topK,
        withWeight=True,
        allowPOS=('n', 'vn', 'nt','ns','nz')
    )
    return keywords

# 为所有文本预处理并提取关键词
all_keywords = []
for text in df['text']:
    keywords = extract_keywords(text)
    for word, weight in keywords:
        all_keywords.append((word, weight))

# 统计关键词频率（带权重）
keyword_counter = Counter()
for word, weight in all_keywords:
    keyword_counter[word] += weight

# 获取前50个最常出现的关键词
top_keywords = dict(keyword_counter.most_common(50))
print("\n出现频率最高的50个关键词：")
for i, (word, freq) in enumerate(list(top_keywords.items())[:50]):
    print(f"{i+1}. {word}: {freq:.2f}")

top_20 = dict(keyword_counter.most_common(20))
words = list(top_20.keys())
freqs = list(top_20.values())

plt.figure(figsize=(14, 8))
bars = plt.barh(words, freqs, color=plt.cm.plasma(np.linspace(0.2, 0.8, len(words))))
plt.xlabel('加权频率', fontsize=12)
plt.title('财经新闻关键词（核心主题）频率排名', fontsize=16)
plt.gca().invert_yaxis()  # 最高频在顶部

# 添加数据标签
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.1, bar.get_y() + bar.get_height()/2,
             f'{width:.1f}',
             va='center', ha='left', fontsize=10)

plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f'finance_keywords_bar_{today}.png', dpi=300)
print("条形图已保存为 financial_keywords_bar.png")
plt.show()

# 情感分析 用snownlp
# snownlp非标准库需要下载 可以使用国内国内镜像下载快些 pip install -i https://pypi.mirrors.ustc.edu.cn/simple/ snownlp
from snownlp import SnowNLP
df['sentiments']=df['title'].apply(lambda x:SnowNLP(x).sentiments)
# 评分越高越积极区间为【0，1】
# 情感标签 消极 积极 中性
df['sentiment_label'] = df['sentiments'].apply(lambda x: '积极' if x > 0.6 else '消极' if x < 0.4 else '中性')

# 情感分布饼图
sentiment_counts = df['sentiment_label'].value_counts()
plt.figure(figsize=(8, 6))
plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%')
plt.title('财经新闻情感分布')
plt.show()