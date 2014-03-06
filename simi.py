#-*- coding: UTF-8 -*- 
import urllib2,urllib,sys



msg = sys.argv[1]

header = {
			'Accept':' */*',
			'Accept-Encoding':'gzip,deflate,sdch',
			'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
			'Connection':'keep-alive',
			'Content-Type':'application/x-www-form-urlencoded',
			'Host':'www.xiaohuangji.com',
			'Referer':'http://www.xiaohuangji.com/',
            'Origin':'http://www.xiaohuangji.com',
            'DNT':'1',
            'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.52 Safari/537.36',
			'X-Requested-With':'XMLHttpRequest'}
data = {'para':msg}
data = urllib.urlencode(data)
#url = 'http://116.255.137.131/ajax.php'
url = 'http://www.xiaohuangji.com/ajax.php'
req = urllib2.Request(url,data=data,headers=header)

response = urllib2.urlopen(req).read()
print response

