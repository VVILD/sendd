
import MySQLdb as mdb
import easypost
import json
import re
import datetime
import json
import time
import dateutil.parser
import urllib
str1=" FedEx"

str2=" to FedEx"


easypost.api_key = 'UX9cFcEOVCEvw32QgFjXBg'


while(1):
	time.sleep(10)
	con = mdb.connect('localhost', 'root', 'followshyp', 'myapp')
	cur=con.cursor()
	cur.execute("SELECT s.mapped_tracking_no,s.company,s.tracking_data,s.tracking_no from myapp_shipment as s where s.status = 'P' and s.company='D'")
	y= cur.fetchall()

	for row in y:
		time.sleep(10)
		awbno=row[0]
		comp=row[1]
		completed=False
		if(awbno!=""):
			if (comp=="D"):

				l=[]
				
				link = "http://track.delhivery.com/p/"+ awbno
				f = urllib.urlopen(link)
				myfile = f.read()
				
				from BeautifulSoup import BeautifulSoup as BSHTML
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
						if (y1=='Delivered'):
							completed=True


				print json.dumps(l)

				cur.execute ("UPDATE myapp_shipment SET tracking_data='%s' WHERE tracking_no=%s" % (json.dumps(l),row[3]))
				con.commit()

				if (completed):
					print "fuck"
					C="C"
					cur.execute ("UPDATE myapp_shipment SET status='C' WHERE tracking_no=%s" % (row[3]))
					con.commit()	
	con.close()




'''
				for x in tracker['tracking_details']:
					time.sleep(1)
					msg=str(x['message'])
					date=str(x['datetime'])
					ur = dateutil.parser.parse(date)
					date= str(ur)[:-6]
					city=x['tracking_location']['city']
					state=x['tracking_location']['state']
					country=x['tracking_location']['country']
					zip=x['tracking_location']['zip']
					if (str(city)=='None'):
						loc="---"
					else:
						loc=str(city)+", " +str(state) + ", "+ str(country) + " -" +str(zip)
					msg=re.sub(str2,"",msg)
					msg=re.sub(str1,"",msg)


					l.append({"status":msg,"date":date,"location":loc})
					'''
'''
					if (msg=='Delivered'):
						print "fuck"
						C="C"
						print row[5]
						cur.execute ("UPDATE myapp_shipment SET status='C' WHERE tracking_no=%s" % (row[5]))
						con.commit()	
'''
