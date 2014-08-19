#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os,time,csv
from multiprocessing.dummy import Pool as ThreadPool

'''
  config files : ip.list , black.list , exclude
'''

HOSTS = {}
BLACKLIST = {}
INTERVAL = '0.1'
COUNT = '10'
PATH = '/nms/bin/'
NOW = time.strftime('%Y/%m/%d-%H:%M',time.localtime(time.time()))

def sping(ip):
	""" do ping ,return a tuple """
	global INTERVAL
	global COUNT

	data = os.popen('ping '+ip+' -c '+COUNT+' -i '+INTERVAL).read()
	loss = data.split('%')[0].split(' ')[-1]
	try:
		rtt = data.split('min/avg/max/mdev =')[1].split()[0]
		min, avg, max, mdev = rtt.split('/')
	except:
		min = avg = max = mdev = '0'
	return (ip,loss,min,avg,max,mdev)

def globalVar(PATH):
	""" create {ip:hostname} and blacklist """
	global HOSTS
	global BLACKLIST

	ipfile = PATH.rstrip('/') + '/ip.list'
	black = PATH.rstrip('/') + '/black.list'
	exclude = PATH.rstrip('/') + '/exclude'

	with open(ipfile,'r') as data:
		for i in data:
			ip,name = i.split(',')
			HOSTS[ip.strip()]=name.strip()
	try:
		blacklist = open(black,'r')
	except:
		os.mknod(black)
		blacklist = open(black,'r')
	BLACKLIST = [i.split()[0].strip() for i in blacklist]

	try:
		excludes = open(exclude,'r')
	except:
		os.mknod(exclude)
		excludes = open(exclude,'r')
	for i in excludes:
		BLACKLIST.append(i.strip())

def alert(msg, warn, type='both'):
	""" msg is (ip,loss,min,avg,max,mdev), from sping() """

	ip,loss,min,avg,max,mdev = msg
	nms = os.uname()[1]
	tpl = '%s:%s [%s] %s | %s%% | %sms' %(nms.strip().upper(),NOW,HOSTS[ip].strip().upper(),ip,loss,avg)
	log = 'time=%s, ip=%s, loss=%s, min=%s, avg=%s, max=%s, mdev=%s' % (NOW,ip,loss,min,avg,max,mdev)
	logging(log)		
	if float(loss) > float(warn) and ip not in BLACKLIST:
		if type == 'mail':
			os.popen('echo "'+tpl+'" | /nms/bin/syslog-sendmail.sh')
		elif type == 'sms':
			os.popen('echo "'+tpl+'" | /nms/bin/syslog-sendsms.sh')
		else:
			os.popen('echo "'+tpl+'" | /nms/bin/syslog-sendmail.sh')
			os.popen('echo "'+tpl+'" | /nms/bin/syslog-sendsms.sh')
		wrBlacklist(ip,PATH)
	return tpl

def logging(log):
	filename = time.strftime('%Y%m%d-%H%M',time.localtime(time.time()))
	pname = time.strftime('%Y%m%d',time.localtime(time.time()))
	logpath = '/nms/log/sping/'+pname+'/'
	if os.path.exists(logpath):
		pass
	else:
		os.makedirs(logpath)
	os.system('echo "'+log+'" >> '+logpath+filename)

def wrBlacklist(ip):
	os.system('echo '+ip+' auto >> '+PATH.rstrip('/') + '/black.list')

def multiTask(count,list):
	
	warn = '30'
	access_warn = '70' 
	non_warn = '200'

	pool = ThreadPool(int(count))
	datalist = pool.map(sping, list)

	for data in datalist:
        	if HOSTS[ip].startswith('A_'):#ip.list column 2 starts with A_ is access switch
                	alert(data, access_warn)
        	elif HOSTS[ip].startswith('NO_'):#ip.list column 2 starts with NO_ didn't alarm
                	alert(data, non_warn)
        	else:
                	alert(data, warn)
	pool.close()
	pool.join()


if __name__ == '__main__':
	ips = []
	globalVar(PATH) #create a dict {ip,hostname} and a blacklist
	for ip in HOSTS:
		ips.append(ip)

	multiTask(20,ips)

	if NOW.endswith('0'):
		os.system('cat /dev/null > '+PATH.rstrip('/')+'/black.list')
