import poplib
from email import parser
import string
import pysqlite2.dbapi2 as sqlite
import datetime
import re

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
	cx = sqlite.connect('/usr/home/sunran/monitor/monitor.db')
	cu = cx.cursor()
	#cu.execute("select message_id from root_mail order by id desc limit 1")
	#last = cu.fetchone()[0]
	#print 'last'+last
	
	ret = pop.stat()

	x = range(ret[0]-1000,ret[0]+1)
	x.reverse()
	for i in x:
		m = pop.retr(i)
		mail_list=[m]
		mail_list = ['\n'.join(i[1]) for i in mail_list]
		ms = [parser.Parser().parsestr(i) for i in mail_list]
		m = ms[0]
		
		message_id = m.get('message-id')
		subject = m.get('subject')
		date = time_format(m.get('date'))
		
		
		k = string.find(subject,'Traverse') and string.find(subject,'Loss')
		#l = string.find(subject,'Traverse') and string.find(subject,'Status')
		
		#if k+l >= 0:
		if k >= 0:
			try:
				ip = re.findall(r'\d+\.\d+\.\d+\.\d+',subject)[0]
				tup = (message_id,date,subject,ip)
				cu.execute("insert into root_mail(message_id,date,subject,ip) values (?,?,?,?)",tup)
				print 'insert ok'
			except Exception,e:
				print e
				break
		else:
			pass
			#print subject
	cx.commit()
	
retr_mail('user@123.com','pass')
	
