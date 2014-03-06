#!/usr/bin/env python

from sys import argv
from os import makedirs,unlink,sep
from os.path import dirname,exists,isdir,splitext
from string import replace,find,lower
from htmllib import HTMLParser
from urllib import urlretrieve
from urlparse import urlparse,urljoin
from formatter import DumbWriter,AbstractFormatter
from cStringIO import StringIO
class Retriever(object):
	def __init__(self,url):
		self.url=url
		self.file=self.filename(url)
	def filename(self,url,deffile='index.html'):
		parsedurl=urlparse(url,'http:',0)
		path=parsedurl[1]+parsedurl[2]	#weibo.com+/gothack
		ext=splitext(path) #weibo.com/gothack , ''  #split by .
		if ext[1]=='':
			if path[-1]=='/':
				path+=deffile
			else:
				path+='/'+deffile
		ldir=dirname(path)	#weibo.com #before the last /
		if sep != '/':	#default value is /
			ldir=replce(ldir,'/',sep)	#replace  / with sep #(string,old,new)
		if not isdir(ldir):
			if exists(ldir):unlink(ldir)
			makedirs(ldir)
		return path
	def download(self):
		try:
			retval=urlretrieve(self.url,self.file)
		except IOError:
			retval=('***ERROR: invalid URL "%s"' %self.url,)
		return retval
	def parseAndGetLinks(self):
		self.parser=HTMLParser(AbstractFormatter(DumbWriter(StringIO())))
		self.parser.feed(open(self.file).read())
		self.parser.close()
		return self.parser.anchorlist
class Crawler(object):
	count=0
	def __init__(self,url):
		self.q=[url]
		self.seen=[]
		self.dom=urlparse(url)[1]
	def getPage(self,url):
		r=Retriever(url)
		retval=r.download()
		if retval[0]=='*':
			print retval,'skipping parse'
			return
		Crawler.count+=1
		print '\n(',Crawler.count,')'
		print 'URL:',url
		print 'FILE:',retval[0]
		self.seen.append(url)
		try:
			links=r.parseAndGetLinks()
			for eachLink in links:
				if eachLink[:4]!='http' and find(eachLink,'://')==-1:
					eachLink=urljoin(url,eachLink)
				if find(lower(eachLink),'mailto:')!=-1:
					print '....discarded,mailto link'
					continue
				if find(eachLink,'#')!=-1:
					print '....discarded,# found'
					continue
				if eachLink not in self.seen:
					if find(eachLink,self.dom)==-1:
						print '...discarded,not in domain'
					else:
						if eachLink not in self.q:
							self.q.append(eachLink)
							print '...new,add to Q'
						else:
							print 'discarded,already in Q'
		except Exception,e:
			print e
	def go(self):
		while self.q:
			url=self.q.pop()
			self.getPage(url)
def main():
	if len(argv)>1:
		url=argv[1]
	else:
		url=raw_input('enter the url:')
	if not url: return
	rebot=Crawler(url)
	rebot.go()
if __name__=='__main__':
	main()	
