from pysnmp.entity.rfc3413.oneliner import cmdgen
import time,sys

def _human(traffic,time):
    traffic = float(traffic)
    Gb=traffic/1000000000/time
    Mb=traffic/1000000/time
    if Gb > 0.7:return str('%.2f' % Gb)+' Gb/s'
    else: return str('%.2f' % Mb)+' Mb/s'

host = sys.argv[1]
status = {1:'UP',2:'DOWN'}
result = {}
adict=locals()
count = [1,2]
sec = 5

gen = cmdgen.CommandGenerator()
gen.ignoreNonIncreasingOid = True

for i,s in enumerate(count):
    errorIndication,errorStatus,errorIndex,adict['varBinds%s' % (i+1)] = \
        gen.nextCmd(
            cmdgen.CommunityData('public','public',1),
            cmdgen.UdpTransportTarget((host,161)),
            (1,3,6,1,2,1,2,2,1,2),(1,3,6,1,2,1,2,2,1,8),(1,3,6,1,2,1,31,1,1,1,6),(1,3,6,1,2,1,31,1,1,1,10))
            #PORT,STATUS,Traffic In,Traffic Out
    time.sleep(sec)

for i in varBinds1:
    result[str(i[0][1])]={'status':status[i[1][1]],'in':int(i[2][1]),'out':int(i[3][1])}
for i in varBinds2:
    result[i[0][1]]['in'] = _human(int(i[2][1]) - result[i[0][1]]['in'],sec)
    result[i[0][1]]['out'] = _human(int(i[3][1]) - result[i[0][1]]['out'],sec)

for k,v in result.items():
    print k,v









'''
for i in varBinds:
    if i[1][1] == 1:
        print 'Port:'+i[0][1]+'\tStatus:'+status[i[1][1]]+'\tIn:'+_human(i[2][1])+'\tOut:'+_human(i[3][1])
'''
