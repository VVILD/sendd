import urllib
link = "http://track.delhivery.com/p/96510007125"
f = urllib.urlopen(link)
myfile = f.read()
import json

from BeautifulSoup import BeautifulSoup as BSHTML
l=[]
string=''
count=-1
BS=BSHTML(myfile)
for definition in BS.findAll('td'):
	count=count+1
	if (count%5==1):
		print count
		y1=unicode.join(u'\n',map(unicode,definition))
		#string=stri

	if (count%5==2):
		print count
		y2=unicode.join(u'\n',map(unicode,definition))
		#string=string+y+'/'

	if (count%5==4):
		print count
		y3=unicode.join(u'\n',map(unicode,definition))
		#string=string+y+'|'
		print 
		l.insert(0,{"status":y1,"date":y2,"location":y3})

print json.dumps(l)


	

