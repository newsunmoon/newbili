import requests
import json
import os
import jieba
from collections import Counter
import pandas as pd
import re
import string
import streamlit as st
from streamlit_echarts import st_echarts
from streamlit.logger import get_logger

# 设置环境变量，用于防止反爬
os.environ['NO_PROXY'] = 'bilibili.net'

def get_hot_list(limit=20):
    """
    获取哔哩哔哩热榜内容并写入文件
    :param limit: 指定要获取的热榜内容的数量
    :return: 返回热榜内容的列表
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url = 'https://api.bilibili.com/x/web-interface/popular/precious'

    try:
        response = requests.get(url, headers=headers, params={'limit': limit})
        response.raise_for_status()  # 如果响应状态码不是200，将会抛出异常
        data = response.json()

        hot_list = data.get('data', {}).get('list', [])

        # 写入文件
        write_to_file(hot_list)

        return hot_list

    except requests.RequestException as e:
        print(f"请求出现异常: {e}")
        return []

def write_to_file(hot_list):
    """
    将热榜内容写入文件
    :param hot_list: 热榜内容的列表
    """
    file_path = 'bilibili_hot_list.txt'

    with open(file_path, 'w', encoding='utf-8') as file:
        for item in hot_list:
            file.write(f"标题: {item.get('title', '')}\n")
            file.write(f"话题名称: {item.get('tname', '')}\n")
    print(f"热榜内容已写入文件: {file_path}")

# Streamlit应用主函数
def main():
    st.title('哔哩哔哩热榜词频统计')  # 设置页面标题

    # 调用函数获取热榜内容并保存到文件
    if st.button('获取哔哩哔哩热榜'):
        hot_list = get_hot_list(st.slider('选择获取的热榜内容数量', 1, 100, 20))
        st.write('已获取哔哩哔哩热榜内容')
    else:
        hot_list = []

    # 定义一个函数load_stop_words，用于从文件stop_words.txt中加载停用词列表。
    def load_stop_words():
        stop_words = []
        with open(r'C:\Users\越好\PycharmProjects\pythonProject\python学习\爬虫学习\可视化学习\stop_words.txt', 'r', encoding='utf-8') as f:
            for line in f:
                stop_words.append(line.strip())
        return stop_words

    stopwords = load_stop_words()

    # 读取热榜内容文件
    with open(r'C:\Users\越好\PycharmProjects\pythonProject\python学习\爬虫学习\可视化学习\bilibili_hot_list.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # 使用re.sub函数和正则表达式去除文本中的HTML标签。
    content = re.sub('<[^<]+?>', '', content)

    # 定义一个函数remove_stopwords，用于从文本中去除停用词。
    def remove_stopwords(text, stopwords):
        words = text.split()
        cleaned_words = [word for word in words if word.lower() not in stopwords]
        return ' '.join(cleaned_words)
    cleaned_text = remove_stopwords(content, stopwords)

    # 使用jieba进行分词
    words = jieba.cut(cleaned_text, cut_all=False)
    word_list = list(words)

    # 再次过滤word_list中的停用词
    word_list = [word for word in word_list if word not in stopwords]

    # 统计词频
    word_counts = Counter(word_list)

    # 移除最高频率的词
    if word_counts:
        most_common_word = word_counts.most_common(1)[0][0]
        del word_counts[most_common_word]

    # 创建一个DataFrame来存储词频
    df = pd.DataFrame(list(word_counts.items()), columns=['Word', 'Frequency'])

    # 对DataFrame按照’Frequency’列进行降序排序
    df = df.sort_values(by='Frequency', ascending=False)

    # 将DataFrame保存到CSV文件
    df.to_csv('word_frequencies.csv', index=False, encoding='utf-8-sig')

    # 显示数据表格
    st.write(df.head(20))  # 显示前20行数据

    # 绘制柱状图
    chart_data = df.head(20)  # 选择前20个词频最高的词汇
    st.bar_chart(chart_data.set_index('Word')['Frequency'])  # 绘制柱状图，Word作为X轴，Frequency作为Y轴

# 运行Streamlit应用
if __name__ == '__main__':
    main()