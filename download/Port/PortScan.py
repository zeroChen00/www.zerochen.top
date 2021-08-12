#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    描述：借用端口扫描项目，梳理套接字、多线程（守护进程、线程锁）的简单使用
    author：chen
    date:2021-6-27
"""
import socket
import sys
import queue
import threading

# 全局变量，队列，用来依次存储端口号
q = queue.Queue()


def portScan():
    while not q.empty():
        port = q.get()
        # 设置套接字连接
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置超时重连时间，单位秒，不设置会导致发包速度极慢，默认15秒
        c.settimeout(0.5)
        # connect.ex()会一直尝试连接，连接成功返回0，失败返回错误信息（key值）
        if c.connect_ex((host, port)) == 0:
            print("%s:%d is open" % (host, port))
            s = host + ":" + str(port)
            # 开启进程锁，多线程写入数据
            lock.acquire()
            with open('./ports.txt', 'a') as fp:
                fp.write(s + "\n")
                # 释放锁
            lock.release()
        else:
            print("%s:%d not open" % (host, port))
        # 关闭套接字连接
        c.close()


# 独立执行时的程序入口
if __name__ == "__main__":
    #argv用来接收用户输入，按输入次序分别为argv[0-n],argv[0]表示脚本名
    if len(sys.argv) < 3:
        print("请以以下格式输入：")
        print("python portScan.py ip 线程数")
    host = sys.argv[1]
    thread_num = int(sys.argv[2])
    # 在进程开始前，定义进程锁，不可在进程中定义锁，否则线程自己使用自己的锁，则失去进程锁的意义
    lock = threading.RLock()

    for port in range(1, 65536):
        q.put(port)
    for i in range(thread_num):
        # 开启守护进程
        t = threading.Thread(target=portScan, daemon=True)
        t.start()

    # 设置主进程死循环，方便接收中断信号
    # 因为设置了守护进程，所以主进程结束，子进程也会立刻结束
    while 1:
        pass