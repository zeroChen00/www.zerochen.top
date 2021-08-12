#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    描述：借用网络爬虫脚本，梳理bs4、requests的简单使用
    author：chen
    date:2021-6-27
"""

import requests
from bs4 import BeautifulSoup

# 自定义请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
}


def page_link(url):
    con = ''
    reponse = requests.get(url=url, headers=headers)
    # 获取当前页面编码格式
    code = reponse.encoding
    # 对响应包的内容解码
    page_text = reponse.text.encode(code).decode('gbk')
    # 使用bs获取指定标签内容（需绑定解析器lxml）
    soup = BeautifulSoup(page_text, "lxml").select('.onearcxsbd > p')
    for i in soup:
        # print(i.text)
        con = con + i.text
    return con


# 程序入口
if __name__ == "__main__":
    url = 'https://www.xyyuedu.com/gdmz/sidamingzhu/sgyy/'      # 目标地址
    reponse = requests.get(url=url, headers=headers)            # 获取请求
    # print(reponse.text)
    code = reponse.encoding                                     # 获取编码方式
    # code = reponse.apparent_encoding
    # print(code)
    page_text = reponse.text.encode(code).decode('gbk')         # 先以网页原编码方式编码，在以指定格式解码，注意，数据仅以编码方式存储，但未进行编码
    # print(page_text)

    soup = BeautifulSoup(page_text, "lxml")                     # 创建soup对象并指定解析器
    aAttr = soup.select('.zhangjie2 > li > a')                  # 获得url所在的标签信息
    # print(aAttr)

    for i in aAttr:
        # print(i.text)
        title = i.text
        link = 'https://www.xyyuedu.com' + i['href']        # 获取章节连接
        content = page_link(link)
        print('开始下载 \n' + title)
        # print(title)
        # print(link)
        # print(content)
        with open('./三国演义.txt', 'a', encoding='utf-8') as fp:
            fp.write(title + '\n' + content + '\n\n\n')
            print(title + '\n' + '下载结束' + '\n')