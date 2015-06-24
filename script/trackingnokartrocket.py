



import MySQLdb as mdb
import easypost
import json
import re
import datetime
import json
import time
import dateutil.parser

import urllib


while(1):
	time.sleep(10)
	con = mdb.connect('localhost', 'root', 'followshyp', 'myapp')
	cur=con.cursor()
	cur.execute("select kartrocket_order,mapped_tracking_no,tracking_no from myapp_shipment where kartrocket_order is NOT NULL AND kartrocket_order<>'' AND (mapped_tracking_no is NULL or mapped_tracking_no='')")
	y= cur.fetchall()

	for row in y:
		time.sleep(10)
		kartrocket_order=row[0]
		pk=row[2]


		link = "http://crazymindtechnologies.kartrocket.co/index.php?route=feed/web_api/orders&version=2&key=c20ad4d76fe97759aa27a0c99bff6710&order_id="+kartrocket_order
		f = urllib.urlopen(link)
		myfile = f.read()
		myfiles=json.loads(myfile)
		try:
			for detail in myfiles['orders'][0]['order_history']:
				if detail['awb_code'] is not None:
					print detail['awb_code']
					
					print detail['courier']
					awb=detail['awb_code']
					courier=detail['courier'][0]
					print courier
					
					cur.execute ("UPDATE myapp_shipment SET mapped_tracking_no='%s',company='%s' WHERE tracking_no=%s" % (awb,courier,pk))
					con.commit()
					break
					
		except:
			print "fail"

	con.close()
'''
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

'''
