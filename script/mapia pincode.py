import re

def cleanhtml(raw_html):
  cleanr =re.compile('<.*?>')
  cleantext = re.sub(cleanr,'', raw_html)
  return cleantext


import urllib
link = "http://www.indiamapia.com/744101.html"
f = urllib.urlopen(link)
myfile = f.read()
from BeautifulSoup import BeautifulSoup as BSHTML
string=''
count=-1
BS=BSHTML(myfile)
for definition in BS.findAll('td'):
	#print definition
	count=1+count
	if (count==10):
		#print count
		#print definition
		#print str(definition)
		x=cleanhtml(str(definition))
		print x

	if (count==11):
		#print count
		#print definition
		#print str(definition)
		x=cleanhtml(str(definition))
		print x[1:-1]