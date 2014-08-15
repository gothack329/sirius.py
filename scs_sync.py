# -*- coding: UTF-8 -*-
from sinastorage.bucket import SCSBucket
import hashlib
import sinastorage
import os,sys
import time,datetime

def listBucket():
	Buckets = []
	s = SCSBucket()
	buckets_generator = s.list_buckets()
	for bucket in buckets_generator:
		bucketName = bucket[0]
		bMeta = SCSBucket(bucketName).meta()
		Buckets.append(bMeta)
	return Buckets
	
def listFile(bucketName):
	Files = []
	s = SCSBucket(bucketName)
	files = s.listdir()
	for i in files:
		#i = (name, isPrefix, sha1, expiration_time, modify, owner, md5, content_type, size)
		Files.append(i)
	return Files

def getLocalFile(localdir):
	localFiles = []
	for root,dirs,files in os.walk(localdir):
		for fn in files:
			f =  root.split(localdir)[1]+'/'+fn
			localFiles.append(f)
	return localFiles

def upload_summary(bucketName,localDir):
	files = getLocalFile(localDir)
	s = f = 0
	failFile = []
	for file in files:
		ss,fl,failed = upload(file,bucketName,localDir)
		s += int(ss)
		f += int(fl)
		if failed != None:
			failFile.append(failed)
	return s,f,failFile
	
def upload(f,bucketName,localDir,ss=0,fl=0):
	f = f.strip('/')
	s = SCSBucket(bucketName)
	failed = None
	try:
		result = s.putFile(f,localDir+f)
		print f+' upload success.'
		ss += 1
	except Exception,e:
		fl += 1
		failed = f
	return ss,fl,failed 

def download(f,bucketName,localDir):
	s = SCSBucket(bucketName)
	try:
		r = s[f]
	except Exception,e:
		print 'Download %s failed' % f
		print e 
		return f
	CHUNK = 16 * 1024
	path = f.split('/')
	if len(path) > 1:
		for i in range(1,len(path)):
			fp = localDir+'/'.join(path[:i])
			if not os.path.exists(fp):
				os.makedirs(fp)
	with open(localDir+f,'wb') as fp:
		while True:
			chunk = r.read(CHUNK)
			if not chunk:break
			fp.write(chunk)	
	print 'Download %s' % f

def scs_sha1(bucketName):
	files = listFile(bucketName)
	info = {}	
	for f in files:
		name, isPrefix, sha1, expiration_time, modify, owner, md5, content_type, size = f
		#info[name.encode('utf-8')] = {'isPrefix':isPrefix,'sha1':sha1,'expiration_time':expiration_time,'modify':modify,'owner':owner,'md5':md5,'content_type':content_type,'size':size}
		info[name.encode('utf-8')] = {'sha1':sha1,'modify':modify}
	return info

def local_sha1(bucketName,localDir):
	mtime = time.strftime('%Y/%m/%d-%H:%M',time.gmtime()) 
	files = getLocalFile(localDir)
	local_info = {}
	for i in files:
		if i.startswith('/'):pass
		else: i = '/'+i
		path = localDir+i
		modify = time.strftime('%Y/%m/%d-%H:%M',time.gmtime(os.path.getmtime(path)))
		sha1 = hashlib.sha1(open(path).read()).hexdigest()
		local_info[i.strip('/')] = {'sha1':sha1,'modify':modify}
	return local_info
		
def checkSha1(scs_info,local_info,bucketName,localDir):
	#print 'scs: ',scs_info
	#print 'local: ',local_info
	for k,v in local_info.items():
		try:
			s = scs_info[k]
			#print s,v
			if v['sha1'] != s['sha1'] :
				print 'AAA'
				local = datetime.datetime.strptime(v['modify'],'%Y/%m/%d-%H:%M')
				local = time.mktime(local.timetuple())
				scs = time.mktime(s['modify'].timetuple())
				if local - scs > 0:
					upload(k,bucketName,localDir)
				elif local - scs < 0:
					download(k,bucketName,localDir)
			scs_info.pop(k)
		except Exception,e:
			#print 'error:' , e
			upload(k,bucketName,localDir)
	if len(scs_info.keys()) > 0:
		for k in scs_info:
			download(k,bucketName,localDir)		

def single(f,localDir,bucketName):
    f = sys.argv[1]
    local_info = local_sha1(bucketName,localDir)
    scs_info = scs_sha1(bucketName)
    if local_info.has_key(f) and scs_info.has_key(f) :
        if local_info[f]['sha1'] != scs_info[f]['sha1']:
            local = datetime.datetime.strptime(local_info[f]['modify'],'%Y/%m/%d-%H:%M')
            local = time.mktime(local.timetuple())
            scs = time.mktime(scs_info[f]['modify'].timetuple())
            if local - scs > 0: upload(f,localDir,bucketName)
            elif local - scs < 0: download(f,localDir,bucketName)
    elif local_info.has_key(f):
        upload(f,localDir,bucketName)
    elif scs_info.has_key(f):
        download(f,bucketName,localDir)

if __name__ == '__main__':
	sinastorage.setDefaultAppInfo('123456789','08b7fc358e123asfi80fvsf7e3347b8a8fc4e')
#	buckets = listBucket()
#	for one in buckets:
#		fileList = listFile(one['Project'])
	localDir = '/path/to/local/dir/'
	bn = 'bucket'
	#result = upload_summary(bn,localDir)	
	#print 'Uploaded %d, failed %d %s' % result
        if len(sys.argv) >= 2:
            single(sys.argv[1],localDir,bn)
        else:
	    a=scs_sha1(bn)
	    b=local_sha1(bn,localDir)
	    checkSha1(a,b,bn,localDir)
