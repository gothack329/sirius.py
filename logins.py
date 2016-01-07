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
    
    
    
    def searchDevice(self,device_info,_list='None'):
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
        cmd = cmd.strip().strip('/')
        if cmd == '' or cmd == 'help':
            self.cmd_help() 
        elif cmd.startswith('user'):
            self.cmd_user(cmd)
        else:
            self.cmd_help()
    
    def cmd_help(self):
        print '''
***

Commands:

To change username & password, use:

search> /user [username]  
search> Password:*****  

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
    
            while True:
                print '\nNotice: Search sth. from IP or Hostname, input "quit" to quit!\n'
                device_info = raw_input('search>')
    
                if device_info.strip() == 'quit':
                    sys.exit()
                    print 'Bye!'
                if device_info.startswith('/'):
                    self.runcmd(device_info)
                else:
                    break
    
            device_list=self.searchDevice(device_info)
    
            if len(device_list) == 1:
                ip, hostname = device_list[0].split(',')
            elif len(device_list) == 0:
                print 'No Device found!'
                continue
            else:
                while True:
                    for i in device_list:
                        print '['+str(device_list.index(i))+'] '+i.strip()
                    print '\nNotice: Input device Number , or start with "/" to search!'
                    device_index = raw_input('select$')
                    if device_index.startswith('/'):
                        device_list=self.searchDevice(device_index.strip('/'),device_list)
                        if len(device_list) == 1:
                            selected = device_list[0]
                            break
                        continue
                    elif device_index.strip() == 'quit':
                        break
                    try:
                        selected = device_list[int(device_index)]
                        break
                    except:
                        continue
                if device_index.strip() == 'quit':
                    continue
        
                ip, hostname = selected.split(',')
    
            result = self.ssh(ip.strip())
            if 'port 22: Connection refused' in str(result):
                self.ssh(ip.strip(),'2222')
        
        
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


