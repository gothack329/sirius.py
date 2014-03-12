#-*- coding: UTF-8 -*-  
import poplib
from email import parser
import pysqlite2.dbapi2 as sqlite
import string
import datetime
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib
import time

def time_format(TIME):
	ISOTIMEFORMAT = '%Y-%m-%d %X'
	GMT_FORMAT = '%a, %d %b %Y %H:%M:%S +0800'
	a = datetime.datetime.strptime(TIME,GMT_FORMAT)
	return a.strftime(ISOTIMEFORMAT)

def retr_mail(username,password):
	"""Login"""
	server = 'mail.staff.sina.com.cn'
	pop = poplib.POP3_SSL(server)
	pop.set_debuglevel(1)
	pop.user(username)
	pop.pass_(password)
	
	"""SQL"""
	cx = sqlite.connect('/usr/home/sunran/monitor/watchtower.db')
	cu = cx.cursor()
	"""clear all data before retr mail"""
	cu.execute("delete from root_mail")
	#cu.execute("select message_id from root_mail order by id desc limit 1")
	#last = cu.fetchone()[0]
	#print 'last'+last
	
	ret = pop.stat()
	print ret
	x = range(1,ret[0]+1)
	x.reverse()
	for i in x:
		m = pop.retr(i)
		pop.dele(i)
		mail_list=[m]
		mail_list = ['\n'.join(i[1]) for i in mail_list]
		ms = [parser.Parser().parsestr(i) for i in mail_list]
		m = ms[0]
		
		message_id = m.get('message-id')
		subject = m.get('subject')
		date = time_format(m.get('date'))
		
		
		k = string.find(subject,'Traverse')
		
		if k > 0:
			try:
				tup = (message_id,date,subject)
				cu.execute("insert into root_mail(message_id,date,subject) values (?,?,?)",tup)
				print 'insert ok'
			except Exception,e:
				print e
				break
		else:
			pass
			#print subject
	print 'finish'
	pop.quit()
	cx.commit()
	
def classify():
	loss={}
	status={}
	traffic={}
	error={}
	cpu={}

	'''get all data'''
	cx = sqlite.connect('/usr/home/sunran/monitor/watchtower.db')
	cu = cx.cursor()
	cu.execute('delete from root_count')
	cu.execute('select subject from root_mail')
	data = cu.fetchall()
	
	for i in data:
		l = string.find(i[0],'Loss')
		s = string.find(i[0],'Status')
		t = string.find(i[0],'Traffic')		
		e = string.find(i[0],'Error') 
		c = string.find(i[0],'CPU') 
		if l > 0:
			if loss.has_key(i):loss[i]+=1
			else: loss[i]=1
		if s > 0:
			if status.has_key(i):status[i]+=1
			else: status[i]=1	
		if t > 0:
			if traffic.has_key(i):traffic[i]+=1
			else: traffic[i]=1
		if e > 0:
			if error.has_key(i):error[i]+=1
			else: error[i]=1
                if c > 0:
                        if cpu.has_key(i):cpu[i]+=1
                        else: cpu[i]=1


	for i in loss:
		try:
			tup = ('loss',i[0],loss[i])
			cu.execute("insert into root_count(type,subject,num) values (?,?,?)",tup)
			#print 'loss'
		except Exception,e:
			print e	
        for i in status:
                try:
                        tup = ('status',i[0],status[i])
                        cu.execute("insert into root_count(type,subject,num) values (?,?,?)",tup)
                        #print 'status'
                except Exception,e:
                        pass

        for i in traffic:
                try:
                        tup = ('traffic',i[0],traffic[i])
                        cu.execute("insert into root_count(type,subject,num) values (?,?,?)",tup)
                        #print 'traffic'
                except Exception,e:
                        pass

        for i in error:
                try:
                        tup = ('error',i[0],error[i])
                        cu.execute("insert into root_count(type,subject,num) values (?,?,?)",tup)
                        #print 'error'
                except Exception,e:
                        pass	
        for i in cpu:
                try:
                        tup = ('CPU',i[0],cpu[i])
                        cu.execute("insert into root_count(type,subject,num) values (?,?,?)",tup)
                        #print 'error'
                except Exception,e:
                        pass

	cx.commit()


def sendmail(user,passwd):
	content = '<p>更多请访问 <a href="http://172.16.118.110/traverse/">http://172.16.118.110/traverse/</a><p>'+urllib.urlopen('http://172.16.118.110/traverse/').read().split('<!--content-->')[1]
	mail_from='pmnpc@staff.sina.com.cn'
	mail_to=['netpm@staff.sina.com.cn','jinjiang@staff.sina.com.cn','xiaoyue1@staff.sina.com.cn','zhuxing@staff.sina.com.cn']
	#mail_to=['sunran@staff.sina.com.cn']
	msg=MIMEMultipart('alternative')
	msg['subject']=u'[Traverse Alert Summary 每日报警汇总]-'+time.strftime('%Y/%m/%d')
	msg['from']='pmnpc@staff.sina.com.cn'
	msg['to']=';'.join(mail_to)
	msg['date']=time.strftime('%a, %d %b %Y %H:%M:%S %z')
	html=MIMEText(content,'html',_charset='utf8')
	msg.attach(html)

	smtp=smtplib.SMTP()
	smtp.connect('mail.staff.sina.com.cn')
	smtp.login(user,passwd)
	smtp.sendmail(mail_from,mail_to,msg.as_string())
	smtp.quit()

retr_mail('pmnpc@sina.com.cn','pass')
classify()	
sendmail('pmnpc','pass')

