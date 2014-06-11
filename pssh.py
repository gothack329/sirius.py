#coding:utf-8
import pexpect
import getpass
import time
import sys

def ssh_cmd(ip, user, passwd, cmds):
    '''cmds is a command list'''
    prompt = '[$#>\]]'
    ssh = pexpect.spawn('ssh %s@%s ' % (user, ip))
    try:
        i = ssh.expect(['continue connecting (yes/no)?','[pP]assword:'],timeout=3)
        if i == 0 :
            ssh.sendline('yes')
            ssh.expect('[pP]assword:')
            ssh.sendline(passwd)
        elif i == 1:
            ssh.sendline(passwd)
    except pexpect.TIMEOUT:
        print 'connected timeout!'
        ssh.close()
    except pexpect.EOF:
        ssh.close()

    vendor = ssh.expect(['Nexus', 'Hangzhou H3C'],timeout=2)
    if vendor == 0:
        pass
        #print 'NX-OS'
    elif vendor == 1:
        pass
        #print 'H3C'
    
    ssh.expect(prompt,timeout=2)
    for cmd in cmds:
        ssh.sendline(cmd)
        ssh.expect(prompt,timeout=5)
        time.sleep(1)
        print '--------%s  :  %s--------' % (ip,cmd)
	print ssh.before.lstrip(cmd)
        print ''
    ssh.close()

def usage():
    print '\n\tUsage : python %s username\n' % sys.argv[0]
    sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()

    user = sys.argv[1]
    passwd = getpass.getpass() 
    hosts = []
    cmds = []

    with open('hosts.ip','r') as hostfile:
        for i in hostfile:
            hosts.append(i.strip())
    with open('cmds.txt','r') as commands:
        for i in commands:
            cmds.append(i.strip())

    for host in hosts:
        ssh_cmd(host,user,passwd,cmds)
