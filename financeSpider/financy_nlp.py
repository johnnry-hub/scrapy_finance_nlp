# -*- coding: utf-8 -*-
import re
import pandas as pd
import datetime
import jieba
import jieba.posseg as psg
import jieba.analyse
from collections import Counter
from snownlp import SnowNLP
from datetime import timedelta

today = datetime.date.today()
# 配置停用词与词典
with open('stopwords.txt', 'r', encoding="utf-8") as f:
    stopwords = set(f.read().split())
    # 手动添加停用词
    stopwords = stopwords.union(
        {'财联社'})  # 临时添加
    # 优化 用set（）把数据转换成无序的集合 能提高数据的运行速度
    # 添加词组使分词更准确
    jieba.initialize()  # 显式初始化 将初始化耗时提前，后续分词无延迟
    jieba.load_userdict('add_word.txt')# 加载自定义词典

# 数据预处理
def process_data(text):
    # 去除特殊符号
    pattern = re.compile('[^\u4e00-\u9fa5a-zA-Z0-9]')
    text= re.sub(pattern, " ", text)

    return text

# # 1、词频分析（取前十）
def process_freq(text):

    try:
        # 过滤停用词和单字
        words = [w for w in jieba.cut(text) if w not in stopwords and len(w)>1]
        word_counts = Counter(words)
        word_freq = ",".join([w for w, _ in word_counts.most_common(10)])
    except Exception as e:
        word_freq = ""
    return word_freq

# 2、词性筛选后的分词
def process_words(text):

    # 名词(n) - 核心内容词（如：中国、经济、市场）
    # 动词(v) - 描述行为和变化（如：增长、下跌、分析）
    # 名动词(vn) - 动词性质的名词（如：发展、影响、改革）
    # 名形词(an) - 形容词性质的名词（如：安全、困难）
    # 专有名词(nr, ns, nt) - 人名、地名、机构名
    # 情感分析需要的词性
    # 形容词(a)
    # 副词(d) - 特别是程度副词（如：非常、极其）
    # 否定词(neg) - （如：不、没、非）
    # 情感动词(v) - （如：喜欢、讨厌、支持）
    flag_list = ['n','vn','ns','nr','nt']
    word_list = []
    # jieba分词
    seg_list = psg.cut(text)
    for seg_word in seg_list:
        word = seg_word.word
        # 去除停用词，单个词以及词性在范围内
        if word not in stopwords and len(word) > 1 and seg_word.flag in flag_list:
            word_list.append(word)
    words = " ".join(word_list)
    # print(words)
    return words

    # 3. 关键词提取（TF-IDF）tf-idf=词频*逆文档频率，通俗易懂的意思就是在本文出现频率多但是在别的文章出现频率少
def process_keywords(text):
    keywords = jieba.analyse.extract_tags(
        text, topK=5, withWeight=False, allowPOS=('n', 'vn', 'ns','nr','nt')  # 保留名词、动名词、地名、人名,机构名
    )
    return keywords

# 5. 情感分析（SnowNLP）
def process_sentiment(text):
    sentiment = SnowNLP(text).sentiments
    if sentiment > 0.6:
        sentiment_type = '积极'
    elif sentiment > 0.4:
        sentiment_type = '中性'
    else:
        sentiment_type ='消极'
    # print (f"情感分析结果:{sentiment_type}:{sentiment:.2f}\n")
    result =f'{sentiment_type}:{sentiment:.2f}'
    return result

def main():
    # 数据清洗
    # 删除缺失值
    df =pd.read_csv(f'finance_news_{today}.csv',encoding='utf-8',).dropna()
    # drop_duplicates删除重复行
    df= df.drop_duplicates()
    # 字段名称列表
    headers = ['url','title','source','source_url','content', 'news_source','update_time']
    # 为数据添加字段名称
    df.columns = headers
    # 删除content里是none的数据
    df=df[df['content']!='none']
    # print(df.info())
    # 提取需要的字段 url,title,content,source,update_time
    df = df[['url', 'title','content', 'source','update_time']]  # 双括号创建列名的列表
    # print(df.info())
    # 筛选24小时内的新闻
    now = datetime.datetime.now()
    hour24 = now - timedelta(days=1)
    df=df[df['update_time']>hour24.strftime('%Y-%m-%d %H:%M')]  # 格式化为年-月-日 时:分
    # print(df.info())
#     进行数据预处理
    df['text']=df['content'].apply(lambda x:process_data(x))
#  词频分析（取前十）
    df['word_freq_top10']=df['text'].apply(lambda x:process_freq(x))
# 词性筛选后的分词
    df['words'] = df['text'].apply(lambda x: process_words(x))
# 提取关键词
    df['keywords'] = df['text'].apply(lambda x: process_keywords(x))

# # 情感分析
    df['sentiment'] = df['text'].apply(lambda x: process_sentiment(x))
    # 删除没用的字段 text
    df = df.drop(columns=['text'])

    #  写入CSV文件
    df.to_csv(f'financy_nlp_{today}.csv', index=False, encoding='utf-8-sig')

    print(f"处理完成！已保存到 financy_nlp_{today}.csv，共 {len(df)} 条记录")

    # print (df.head())
    # print (df.info())

if __name__ == '__main__':
    main()






