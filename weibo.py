#!/usr/bin/env python  
# -*- coding: utf-8 -*- 
import sys  
import os
from bs4 import BeautifulSoup as bs
import sqlite3
import urllib,urllib2
from instapush import Instapush, App

reload(sys)   
sys.setdefaultencoding('utf8')  



def weibo(uid):
    #cu.execute("create table weibo (id integer primary key AUTOINCREMENT,username varchar(512),linkid varchar(32) UNIQUE,time varchar(64),content varchar(1024))")
    
    html=os.popen('curl http://service.weibo.com/widget/widget_blog.php\?\uid='+str(uid)).read()
    
    cx = sqlite3.connect("/root/script/weibo.db")
    cu=cx.cursor()
    
    #cx.execute("insert into weibo values (?,?,?,?)", (username,linkid,time,content))
    linkids = cu.execute("select linkid from weibo").fetchall()
    linkids = [x[0] for x in  linkids]
    
    soup = bs(html)
    username = soup.find('div',{'class':'userNm txt_b'}).text
    p = soup.find_all('p',{'class':'wgtCell_txt'})
    a = soup.find_all('a',{'class':'link_d'})
    linkid = soup.find_all('a',{'class':'link_d'})
    
    
    for i in range(len(a)):
        id = linkid[i].attrs['href'].split('/')[-1]
        time = a[i].text
        content = p[i].text.replace('  ','').replace('\r','').replace('\n','').strip()
        if id in linkids:
            cx.execute('update weibo set time="'+time+'" where linkid="'+id+'"')
            continue
        else:
            pass
        print time,content
        try:
            cx.execute("insert into weibo values (?,?,?,?,?)", (None,username,id,time,content))
        except Exception,e:
            print e
        instapush(username,time,content)
    
    cx.commit()
    return



def instapush(username,time,content):
    app = App(appid='appid',secret='app secret')
    app.notify(event_name='Weibo',trackers={"username":username,"time":time,"weibo":content})
    return



if __name__ == '__main__':
    weibo(1223920903)
    #instapush('username','time','instapush')

