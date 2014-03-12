#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os,time,csv

now = time.strftime('%Y/%m/%d-%H:%M',time.localtime(time.time()))
today = time.strftime('%Y%m%d',time.localtime(time.time()))
idc = 'ja'
ip_list =[]
ips = open('/usr/home/sunran/csv/ip.list','r')
for i in ips:
        ip_list.append(i.strip())

csvfile = '/usr/home/sunran/monitor/static/'+idc+'-'+today+'.csv'
try:
	blacklist = open('/usr/home/sunran/csv/black.list','r')
except:
	os.mknod('/usr/home/sunran/csv/black.list')
	blacklist = open('/usr/home/sunran/csv/black.list','r')
blacklist = [i.split()[0].strip() for i in blacklist]
count = '10'

exclude = open('/usr/home/sunran/csv/exclude','r')
for i in exclude:
	blacklist.append(i.strip())
print blacklist

write_line = [now]

for ip in ip_list:
        data = os.popen('ping '+ip+' -c '+count+' -i 0.2').read()
        loss = data.split('%')[0].split(' ')[-1]
	try:
		delay = data.split('min/avg/max/mdev =')[1].split('/')[1]
	except:
		delay = 'NONE'
        write_line.append(loss)
        print ip,loss
	if int(loss) >= 30 and ip not in blacklist:
		print os.popen('''/aaa/bin/nms-alert.py -m "IP:'''+ip+'''\n丢包率:'''+loss+'''%\n延时:'''+delay+''' ms" -r nms -R -s " " -a 'email,sms' ''').read()
		os.system('echo '+ip+' auto >> /usr/home/sunran/csv/black.list')
		print ip
try:
        reader = csv.reader(file(csvfile,'rb'))
        writer = csv.writer(file(csvfile,'ab'))
        writer.writerow(write_line)
except:
        writer = csv.writer(file(csvfile,'wb'))
        ip_list.insert(0,'Time')
        filedname = ip_list
        writer.writerow(filedname)
        writer = csv.writer(file(csvfile,'ab'))
        writer.writerow(write_line)

if now.endswith('0'):
	os.system('cat /dev/null > /usr/home/sunran/csv/black.list')

