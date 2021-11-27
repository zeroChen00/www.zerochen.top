# 原始项目地址：https://github.com/Threezh1/JSFinder
# 原始项目作者：https://threezh1.github.io/
# 改进: by 沉墨
# 修改:
#   修复不传参显示bug
#   新增ip:port抓取
#	删除-d参数--抓取全部url链接中的数据，意义不大
#   优化代码可读性
# date: 2021.11.21

import requests, argparse, sys, re
from requests.packages import urllib3
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def parse_args():
	parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -u http://www.baidu.com")
	parser.add_argument("-u", "--url", help="The website")
	parser.add_argument("-c", "--cookie", help="The website cookie")
	parser.add_argument("-f", "--file", help="The file contains url or js")
	parser.add_argument("-ou", "--outputurl", help="Output file name. ")
	parser.add_argument("-os", "--outputsubdomain", help="Output file name. ")
	parser.add_argument("-oi", "--outputip", help="Output file name. ")
	parser.add_argument("-j", "--js", help="Find in js file", action="store_true")
	return parser.parse_args()


# 抓取js文件中的网页链接
def extract_URL(JS):
	pattern_raw = r"""
	  (?:"|')                               # Start newline delimiter
	  (
		((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
		[^"'/]{1,}\.                        # Match a domainname (any character + dot)
		[a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
		|
		((?:/|\.\./|\./)                    # Start with /,../,./
		[^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
		[^"'><,;|()]{1,})                   # Rest of the characters can't be
		|
		([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
		[a-zA-Z0-9_\-/]{1,}                 # Resource name
		\.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
		(?:[\?|/][^"|']{0,}|))              # ? mark with parameters
		|
		([a-zA-Z0-9_\-]{1,}                 # filename
		\.(?:php|asp|aspx|jsp|json|
			 action|html|js|txt|xml)             # . + extension
		(?:\?[^"|']{0,}|))                  # ? mark with parameters
	  )
	  (?:"|')                               # End newline delimiter
	"""
	pattern = re.compile(pattern_raw, re.VERBOSE)
	result = re.finditer(pattern, str(JS))
	if result is None:
		return None
	js_url = []
	return [match.group().strip('"').strip("'") for match in result if match.group() not in js_url]


# 匹配js文件中的ip
def extract_IP(JS):
	# 匹配ip:port
	pattern_raw = r"""
	  (((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}[:\d+]*)
	"""
	pattern = re.compile(pattern_raw, re.VERBOSE)
	result = re.finditer(pattern, str(JS))
	if result is None:
		return None
	js_ip = []
	js_ip = list(set([match.group().strip('"').strip("'") for match in result if match.group() not in js_ip]))
	return js_ip


# 页面源码
def Extract_html(URL):
	header = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
		"Cookie": args.cookie}
	try:
		raw = requests.get(URL, headers=header, timeout=3, verify=False)
		raw = raw.content.decode("utf-8", "ignore")
		# print(raw)
		return raw
	except:
		return None


# 处理网址
def process_url(URL, re_URL):
	black_url = ["javascript:"]
	URL_raw = urlparse(URL)
	ab_URL = URL_raw.netloc
	host_URL = URL_raw.scheme
	if re_URL[0:2] == "//":
		result = host_URL + ":" + re_URL
	elif re_URL[0:4] == "http":
		result = re_URL
	elif re_URL[0:2] != "//" and re_URL not in black_url:
		if re_URL[0:1] == "/":
			result = host_URL + "://" + ab_URL + re_URL
		else:
			if re_URL[0:1] == ".":
				if re_URL[0:2] == "..":
					result = host_URL + "://" + ab_URL + re_URL[2:]
				else:
					result = host_URL + "://" + ab_URL + re_URL[1:]
			else:
				result = host_URL + "://" + ab_URL + "/" + re_URL
	else:
		result = URL
	return result


def find_last(string, str):
	positions = []
	last_position = -1
	while True:
		position = string.find(str, last_position + 1)
		if position == -1: break
		last_position = position
		positions.append(position)
	return positions


# 获取url中js的路径，然后提取其中的url
def find_by_url(url):
	html_raw = Extract_html(url)
	if html_raw is None:
		print("Fail to access " + str(url))
		return None
	else:
		print("Start: " + str(url) + "  ...\n")
	html = BeautifulSoup(html_raw, "html.parser")
	html_scripts = html.findAll("script")  # script标签内容
	script_array = {}
	script_temp = ""
	for html_script in html_scripts:  # html_script: script数据
		script_src = html_script.get("src")
		if script_src is None:
			script_temp += html_script.get_text() + "\n"  # script_temp: script正文内容（去除标签）
		else:
			purl = process_url(url, script_src)  # purl: js文件链接
			script_array[purl] = Extract_html(purl)  # script_array[purl]: js链接页面源码
	script_array[url] = script_temp  # js文件数据存入script_array[url]

	allurls = []  # 所有网页链接
	allips = []  # 所有网页ip
	# 获取url
	for script in script_array:
		temp_urls = extract_URL(script_array[script])  # js文件中的url
		if len(temp_urls) == 0: continue
		for temp_url in temp_urls:
			allurls.append(process_url(script, temp_url))

	# 获取ip
	for script in script_array:
		temp_ips = extract_IP(script_array[script])  # js文件中的url
		if len(temp_ips) == 0: continue
		for temp_ip in temp_ips:
			allips.append(temp_ip)

	result_url = []
	result_ip = allips
	for singerurl in allurls:
		url_raw = urlparse(url)
		domain = url_raw.netloc
		positions = find_last(domain, ".")
		maindomain = domain
		if len(positions) > 1: maindomain = domain[positions[-2] + 1:]
		suburl = urlparse(singerurl)
		subdomain = suburl.netloc
		if maindomain in subdomain or subdomain.strip() == "":
			if singerurl.strip() not in result_url:
				result_url.append(singerurl)
	return result_url, result_ip


# 提取域名
def find_subdomain(urls, mainurl):
	url_raw = urlparse(mainurl)
	domain = url_raw.netloc
	maindomain = domain
	positions = find_last(domain, ".")
	if len(positions) > 1: maindomain = domain[positions[-2] + 1:]
	subdomains = []
	for url in urls:
		suburl = urlparse(url)
		subdomain = suburl.netloc
		# print(subdomain)
		if subdomain.strip() == "": continue
		if maindomain in subdomain:
			if subdomain not in subdomains:
				subdomains.append(subdomain)
	return subdomains


# 从文件中读取url
def find_by_file(file_path):
	with open(file_path, "r") as fobject:
		links = fobject.read().split("\n")
	if not links: return None
	print("ALL Find " + str(len(links)) + " links")

	urls = []
	ips = []
	i = len(links)
	for link in links:
		temp_urls, temp_ips = find_by_url(link)

		if temp_urls is None: continue
		print(str(i) + " Find " + str(len(temp_urls)) + " URL in " + link)
		for temp_url in temp_urls:
			if temp_url not in urls:
				urls.append(temp_url)

		if temp_ips is None: continue
		print(str(i) + " Find " + str(len(temp_ips)) + " IP in " + link)
		for temp_ip in temp_ips:
			if temp_ip not in ips:
				ips.append(temp_ip)
		i -= 1
	return urls, ips


# 打印结果
def giveresult(urls, ips, domian):
	content_url = ""
	content_subdomain = ""
	content_ip = ""
	if urls is None:
		return None
	print("Find " + str(len(urls)) + " URL:")
	for url in urls:
		content_url += url + "\n"
		print(url)

	subdomains = find_subdomain(urls, domian)
	print("\nFind " + str(len(subdomains)) + " Subdomain:")
	for subdomain in subdomains:
		content_subdomain += subdomain + "\n"
		print(subdomain)

	print("\nFind " + str(len(ips)) + " IP:")
	for ip in ips:
		content_ip += str(ip) + "\n"
		print(ip)

	if args.outputurl is not None:
		with open(args.outputurl, "a", encoding='utf-8') as fobject:
			fobject.write(content_url)
		print("\nOutput " + str(len(urls)) + " urls")
		print("Path:" + args.outputurl)
	if args.outputsubdomain is not None:
		with open(args.outputsubdomain, "a", encoding='utf-8') as fobject:
			fobject.write(content_subdomain)
		print("\nOutput " + str(len(subdomains)) + " subdomains")
		print("Path:" + args.outputsubdomain)
	if args.outputip is not None:
		with open(args.outputip, "a", encoding='utf-8') as fobject:
			fobject.write(content_ip)
		print("\nOutput " + str(len(ips)) + " ips")
		print("Path:" + args.outputip)


if __name__ == "__main__":
	urllib3.disable_warnings()
	args = parse_args()
	if len(sys.argv) == 1:  # 增加无参状态下的帮助信息
		exit("python " + sys.argv[0] + " -h")
	if args.file is None:
		urls, ips = find_by_url(args.url)
		giveresult(urls, ips, args.url)
	else:
		urls, ips = find_by_file(args.file)
		giveresult(urls, ips, urls[0])