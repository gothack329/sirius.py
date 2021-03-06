#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pexpect
import getpass
import time
import sys,os


class logins(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.olduser = username
        self.oldpass = password
        self.conffile = '/home/sunran/script/device'

    def ssh(self, ip, port='22'):
        ssh = pexpect.spawn('ssh %s@%s -p %s ' % (self.username, ip, port))
        ssh.setwinsize(40,130)
        try:
            i = ssh.expect(['continue connecting (yes/no)?','[pP]assword:'],timeout=10)
            if i == 0 :
                ssh.sendline('yes')
                ssh.expect('[pP]assword:')
                ssh.sendline(self.password)
            elif i == 1:
                ssh.sendline(self.password)
        except pexpect.TIMEOUT:
            print 'connected timeout!'
            ssh.close()
        except pexpect.EOF:
            error = ssh.before
            ssh.close()
            return error
    
        ssh.interact()
        print "Thanks!"
        ssh.close()
    
    
    
    def searchDevice(self,device_info='',_list='None'):
        device_info = device_info.lower().replace('_','-')
        if _list == 'None':
            device = open(self.conffile,'r').readlines()
        else:
            device = _list
        result = []
        for i in device:
            if device_info in i.lower().replace('_','-'):
                  result.append(i)
        return result
    
    def runcmd(self,cmd):
        cmd = cmd.strip().strip('$')
        if cmd == '' or cmd == 'help':
            self.cmd_help() 
        elif cmd.startswith('user'):
            self.cmd_user(cmd)
        elif cmd.startswith('show'):
            self.cmd_show(cmd)
        else:
            self.cmd_help()

    def cmd_show(self,cmd):
        print 'Current user is: ',self.username
        print 
    
    def cmd_help(self):
        print '''
***

Commands:

To change username & password, use:

search> $user [username]  
search> Password:*****  

To show current user, use:

search> $show

***
'''

    def cmd_user(self,cmd):
        self.olduser = self.username
        self.oldpass = self.password
        try:
            u,username = cmd.split()
        except:
            print 'Notice: CMD error!'
            self.cmd_help()
            return

        self.username = username
        self.password = getpass.getpass() 
        print 'change user to %s' % (self.username)
        
    def main(self):
        while True:
            history = []
            flag = -2
            device_list = self.searchDevice()
            device_all = device_list
            history.append(device_all)
            print '''\nNotice: 
\texit : exit program
\tend  : all device list
\tq    : previous device list
\t/3   : select device\n'''
            while True:
                notice = '' 
                print '#'
                print ' Devices:'+str(len(device_list))
                print ' Filter times:'+str(len(history))
                print ' Filter length:',str([len(i) for i in history])
                print 
                device_info = raw_input('search>')
    
                if device_info.strip() == 'exit':
                    sys.exit()
                    print 'Bye!'
                elif device_info.strip() == 'q':
                    try:
                        device_list = history[flag]
                        history.pop()
                    except:
                        history = []
                        history.append(device_all)
                    continue
                elif device_info.strip() == 'end':
                    device_list = history[0]
                    history = []
                    history.append(device_all)
                    continue
                elif device_info.startswith('$'):
                    self.runcmd(device_info)
                    continue
                elif device_info.startswith('/'):
                    try:
                        selected = device_list[int(device_info.strip('/'))]
                        break
                    except Exception, e:
                        print e
                        continue
                else:
                    device_list = self.searchDevice(device_info,device_list)
                    history.append(device_list)
    
                    if len(device_list) == 1:
                        selected = device_list[0]
                        break
                    elif len(device_list) == 0:
                        notice = 'No device found!'
                        device_list = history[flag]
                        history.pop()
                        continue
                for i in device_list:
                    print '['+str(device_list.index(i))+'] '+i.strip()
        
            if notice:print notice
            ip, hostname = selected.split(',')
    
            result = self.ssh(ip.strip())
            if 'port 22: Connection refused' in str(result):
                self.ssh(ip.strip(),'51899')
        
        
def usage():
    print '\n\tUsage :  %s username\n' % sys.argv[0]
    sys.exit(0)
    
if __name__ == '__main__':

    if len(sys.argv) < 2:
        usage()

    user = sys.argv[1]
    passwd = getpass.getpass() 
    lg = logins(user,passwd)
    lg.main()

