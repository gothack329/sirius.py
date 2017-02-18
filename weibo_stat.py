#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import re , urllib.parse , urllib.request , http.cookiejar , base64 , binascii , rsa 
from bs4 import BeautifulSoup as bs
import sqlite3
import time,sys
import socks
import socket
import os
from instapush import Instapush, App

class LoginStatus:
    def __init__(self,nick,passwd):
        '''create table status (id integer primary key AUTOINCREMENT,uid varchar(32), username varchar(512),time varchar(32),action varchar(64));'''
        self.nick = nick
        self.passwd = passwd
        socks.set_default_proxy(socks.SOCKS5, "localhost", 7070)
        socket.socket = socks.socksocket

        self.cj = http.cookiejar.LWPCookieJar()
        self.cookie_support = urllib.request.HTTPCookieProcessor(self.cj)
        self.opener = urllib.request.build_opener(self.cookie_support , urllib.request.HTTPHandler) 
        urllib.request.install_opener(self.opener)

    def getData(self , url):
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        text = response.read().decode('utf-8')
        return text

    def postData(self, url , data):
        headers = {'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'}
        data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(url , data , headers)
        response = urllib.request.urlopen(request)
        text = response.read().decode('gbk')
        return text


    def login_weibo(self):
        #========================== get servertime , pcid , pubkey , rsakv===========================
        # pre login
        prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.15)&_=1400822309846' % self.nick
        preLogin = self.getData(prelogin_url)

        servertime = re.findall('"servertime":(.*?),' , preLogin)[0]
        pubkey = re.findall('"pubkey":"(.*?)",' , preLogin)[0]
        rsakv = re.findall('"rsakv":"(.*?)",' , preLogin)[0]
        nonce = re.findall('"nonce":"(.*?)",' , preLogin)[0]
        #===============encode username & password================
        su = base64.b64encode(bytes(urllib.request.quote(self.nick) , encoding = 'utf-8'))
        rsaPublickey = int(pubkey , 16)
        key = rsa.PublicKey(rsaPublickey , 65537)
        message = bytes(str(servertime) + '\t' + str(nonce) + '\n' + str(self.passwd) , encoding = 'utf-8')
        sp = binascii.b2a_hex(rsa.encrypt(message , key))
        #=======================login =======================
        param = {'entry' : 'weibo' , 'gateway' : 1 , 'from' : '' , 'savestate' : 7 , 'useticket' : 1 , 'pagerefer' : 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D' , 'vsnf' : 1 , 'su' : su , 'service' : 'miniblog' , 'servertime' : servertime , 'nonce' : nonce , 'pwencode' : 'rsa2' , 'rsakv' : rsakv , 'sp' : sp , 'sr' : '1680*1050' ,
                 'encoding' : 'UTF-8' , 'prelt' : 961 , 'url' : 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'}
        s = self.postData('http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)' , param)
        try:
            urll = re.findall("location.replace\(\'(.*?)\'\);" , s)[0]
        except Exception as e:
            os.system('start cn proxy')
        self.getData(urll)

    def getStatus(self,uid):
        self.login_weibo()
        now = time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))
        text = self.getData('http://www.weibo.com/aj/user/newcard?id='+str(uid))
        text = text.replace('\\"','"').replace('\\/','/')
        soup = bs(text)
        inner = soup.find('i',{'class':'W_chat_stat'})
        status = inner['class'][1]
        u = [x.split('=')[1] for x in soup.find('a',{'class':'W_btn_c'})['action-data'].split('&')]
        return (None,u[0],u[1],now,status)

    def refresh(self,uid):
        uid = str(uid)
        cx = sqlite3.connect("/root/script/weibo.db")
        cu=cx.cursor()

        last = cu.execute('select max(rowid),action from status where uid=="'+uid+'" ').fetchone()[1]
        data = self.getStatus(uid)
        iid,uid,username,t,status = data
        username = username.encode('latin-1').decode('unicode_escape')
        print(username,status)

        if status != last:
            cu.execute('insert into status values (?,?,?,?,?)',data)
            self.instapush(username,t,status)
        cx.commit()

    def instapush(self,username,time,status):
        action = {'W_chat_stat_online':'上线了','W_chat_stat_offline':'下线了'}
        app = App(appid='appid',secret='secret')
        app.notify(event_name='WeiboStat',trackers={"username":username,"time":time,"status":action[status]})


if __name__ == '__main__':
    weibo = LoginStatus('weibo_username','password')
    weibo.refresh(uid)
