#-*- coding: UTF-8 -*- 

import requests
import urllib2

r = requests.get('http://www.simsimi.com/talk.htm')
cookie = r.cookies
#cookie_proc = urllib2.HTTPCookieProcessor(cookie)
#opener = urllib2.build_opener(cookie_proc)

for i,j in enumerate(cookie):
	print i,j

msg = 'hi'

header = {'Accept':'application/json, text/javascript, */*; q=0.01',
			'Accept':'application/json, text/javascript, */*; q=0.01',
			'Accept-Encoding':'gzip,deflate,sdch',
			'Accept-Language':'zh-CN,zh;q=0.8',
			'Connection':'keep-alive',
			'Content-Type':'application/json; charset=utf-8',
			'Host':'www.simsimi.com',
			'Referer':'http://www.simsimi.com/talk.htm',
			'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36',
			'X-Requested-With':'XMLHttpRequest'}

url = 'http://www.simsimi.com/func/req?msg=%s&lc=ch' % msg

response = requests.get(url,cookies=cookie,headers=header).text.split('response":"')[1].split('"')[0]
print response

