from itertools import product
import os

keywords = ['121','226','89','19','gao','fei','f','g','G','F','0','GAO','FEI'] 
lens = len(keywords)

dic = open('password.txt','a+')
for i in range(2,6):
	outlist = list(product(keywords[:lens],repeat=i))
	for j in outlist:
		result = ''.join([v for v in j])
		dic.write(result+'\n')
dic.close()
os._exit(1)
