import json
import requests, time, re
from faker import Faker
import csv
import urllib
from googletrans import Translator


# 谷歌翻译
def translate(word):
    try:
        translator = Translator(service_urls=['translate.google.com',])
        trans=translator.translate(word, src='auto', dest='zh-cn')
        # print(trans.origin)     # 原文
        # print(trans.text)       # 译文
        return trans.text
    except:
        return word


#main函数
if __name__ == '__main__':
    with open("out.csv", "a", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(['domain', 'title'])

    ms = open("./dd.txt","r",encoding="utf-8")
    for line in ms.readlines():
        try:
            url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', line)[0]
            domain = urllib.parse.urlparse(url).netloc
            words = line.replace(url," ").strip()
            # print("url: " + url + "\n")
            print("domain: " + domain + "\n")
            # print("words: " + words + "\n")
            if words != "":
                tran = translate(words)
                print("tran: " + tran + "\n")
            else:
                tran = words
            with open("out.csv", "a", newline='', encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([domain, tran])
        except:
            continue
    ms.close()