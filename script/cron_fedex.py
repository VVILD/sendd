
import MySQLdb as mdb
import easypost
import json
import re
import datetime
import json
import time
import dateutil.parser

str1=" FedEx"

str2=" to FedEx"


easypost.api_key = 'UX9cFcEOVCEvw32QgFjXBg'


while(1):
	time.sleep(1)
	con = mdb.connect('localhost', 'root', 'followshyp', 'myapp')
	cur=con.cursor()
	cur.execute("SELECT s.mapped_tracking_no,s.company,s.tracking_data,o.date,o.time,s.tracking_no from myapp_shipment as s join myapp_order as o where s.status = 'P'")
	y= cur.fetchall()

	for row in y:
		time.sleep(1)
		awbno=row[0]
		comp=row[1]

		if(awbno!=""):
			if (comp=="F"):
				tracker = easypost.Tracker.create(
				      tracking_code=awbno,
				      carrier="FEDEX"
				  )
				l=[]
				l.append({"status":"Booking Received","date":str(row[3])+ " " + str(row[4]),"location":"Mumbai (Maharashtra)"})		

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
					if (msg=='Delivered'):
						print "fuck"
						C="C"
						print row[5]
						cur.execute ("UPDATE myapp_shipment SET status='C' WHERE tracking_no=%s" % (row[5]))
						con.commit()	


				cur.execute ("UPDATE myapp_shipment SET tracking_data='%s' WHERE tracking_no=%s" % (json.dumps(l),row[5]))
				con.commit()	
	con.close()


