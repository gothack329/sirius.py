from pysnmp.entity.rfc3413.oneliner import cmdgen

host = '192.168.100.1'
gen = cmdgen.CommandGenerator()
gen.ignoreNonIncreasingOid = True

errorIndication,errorStatus,errorIndex,varBinds = \
        cmdgen.CommandGenerator().nextCmd(
            cmdgen.CommunityData('public','public',1),
            cmdgen.UdpTransportTarget((host,161)),
            (1,3,6,1,2,1,2,2,1,2),(1,3,6,1,2,1,2,2,1,10))

for i in varBinds: print 'Port:'+i[0][1]+',In:'+i[1][1]