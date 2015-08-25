from django.core.management.base import BaseCommand
from businessapp.models import Product
from myapp.models import Shipment
import easypost
import aftership
api = aftership.APIv4('c46ba2ea-5a3e-43c9-bda6-793365ec1ebb')
import json
import time
import dateutil.parser
import datetime
import urllib
import re
import datetime	



easypost.api_key = 'UX9cFcEOVCEvw32QgFjXBg'


format='%Y-%m-%d %H:%M:%S'


def remove_non_ascii_1(text):
	return ''.join(i for i in text if ord(i)<128)


class Command(BaseCommand):
  args = 'Arguments is not needed'
  help = 'Django admin custom command poc.'
 
  def handle(self, *args, **options):

#bluedart product

	self.stdout.write("starting bluedart api for bluedart product")
	required_product = Product.objects.filter(Q(company='B')&(Q(status='P')|Q(status='DI'))).exclude(order__status='C')
	slug='bluedart'
	
	for product in required_product:
		print product.mapped_tracking_no
		number=product.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			y=api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data
		except:#tracking number already exist
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data


		for x in data['tracking']['checkpoints']:
			#print x['message']
			#print x['location']
			y1=str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0=remove_non_ascii_1(x['message'])
			str3=x['location'].encode('utf8')
			tracking_data.append({"status":str(str0),"date":str(str1),"location":str(str3)})
			if ('delivered' in str0.lower()):
				print "fucking delivered"
				product.status='C'
				product.save()
				order=product.order
				#getting all products of that order

				specific_products=Product.objects.filter(order=order)
				order_complete=True
				for specific_product in specific_products:
					if specific_product.status=='P':
						order_complete=False

				if (order_complete):
					order.status='C'
					order.save()


				break;

		if (json.dumps(tracking_data)!='[]'):
			product.tracking_data=json.dumps(tracking_data)
			product.save()


#bluedart shipment

	self.stdout.write("starting bluedart api for bluedart shipment")
	required_shipment = Shipment.objects.filter(Q(company='B')&(Q(status='P')|Q(status='DI')))
	slug='bluedart'
	
	for shipment in required_shipment:
		print shipment.mapped_tracking_no
		number=shipment.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			y=api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data
		except:#tracking number already exist
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data


		for x in data['tracking']['checkpoints']:
			#print x['message']
			#print x['location']
			y1=str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0=remove_non_ascii_1(x['message'])
			str3=x['location'].encode('utf8')
			tracking_data.append({"status":str(str0),"date":str(str1),"location":str(str3)})
			if ('delivered' in str0.lower()):
				print "fucking delivered"
				shipment.status='C'
				shipment.save()
				myapp_order=shipment.order
				#getting all products of that order

				specific_shipments=Shipment.objects.filter(order=myapp_order)
				order_complete=True
				for specific_product in specific_shipments:
					if specific_product.status=='P':
						order_complete=False

				if (order_complete):
					myapp_order.order_status='D'
					myapp_order.save()


				break;

		shipment.tracking_data=json.dumps(tracking_data)
		shipment.save()



#bluedart ends


#Aramex PRoduct


	
	self.stdout.write("starting Aramex api for aramex product")
	required_product = Product.objects.filter(Q(company='A')&(Q(status='P')|Q(status='DI'))).exclude(order__status='C')
	slug='aramex'
	
	for product in required_product:
		print product.mapped_tracking_no
		number=product.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			y=api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data
		except:#tracking number already exist
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data


		for x in data['tracking']['checkpoints']:
			#print x['message']
			#print x['location']
			y1=str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0=remove_non_ascii_1(x['message'])
			str3=x['location'].encode('utf8')
			tracking_data.append({"status":str(str0),"date":str(str1),"location":str(str3)})
			if (str0=='Delivered'):
				print "fucking delivered"
				product.status='C'
				product.save()
				order=product.order
				#getting all products of that order

				specific_products=Product.objects.filter(order=order)
				order_complete=True
				for specific_product in specific_products:
					if specific_product.status=='P':
						order_complete=False

				if (order_complete):
					order.status='C'
					order.save()


				break;

		product.tracking_data=json.dumps(tracking_data)
		product.save()

	self.stdout.write("starting Aramex api for aramex shipment")
	required_shipment = Shipment.objects.filter(Q(company='A')&(Q(status='P')|Q(status='DI')))
	slug='aramex'
	
	for shipment in required_shipment:
		print shipment.mapped_tracking_no
		number=shipment.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			y=api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data
		except:#tracking number already exist
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data


		for x in data['tracking']['checkpoints']:
			#print x['message']
			#print x['location']
			y1=str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0=remove_non_ascii_1(x['message'])
			str3=x['location'].encode('utf8')
			tracking_data.append({"status":str(str0),"date":str(str1),"location":str(str3)})
			if (str0=='Delivered'):
				print "fucking delivered"
				shipment.status='C'
				shipment.save()
				myapp_order=shipment.order
				#getting all products of that order

				specific_shipments=Shipment.objects.filter(order=myapp_order)
				order_complete=True
				for specific_product in specific_shipments:
					if specific_product.status=='P':
						order_complete=False

				if (order_complete):
					myapp_order.order_status='D'
					myapp_order.save()


				break;

		shipment.tracking_data=json.dumps(tracking_data)
		shipment.save()


# fedex product



	self.stdout.write("starting fedex api for fedex product")
	required_product = Product.objects.filter(Q(company='F')&(Q(status='P')|Q(status='DI'))).order_by("-order__book_time").exclude(order__status='C')
	#slug='aramex'
	str1=" FedEx"
	str2=" to FedEx"
	for product in required_product:
		print product.mapped_tracking_no
		number=product.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			tracker = easypost.Tracker.create(
				      tracking_code=number,
				      carrier="FEDEX"
				  )			#print data
		#print data


			for x in tracker['tracking_details']:
				time.sleep(1)
				msg=str(x['message'])
				date=str(x['datetime'])
				ur = dateutil.parser.parse(date)
				datestr= str(ur)[:-6]
				#print datestr
				date=datetime.datetime.strptime(datestr,format)
				date=date+ datetime.timedelta(hours=5,minutes=30)
				date=str(date)
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
				tracking_data.append({"status":msg,"date":date,"location":loc})	

				if ('Returning package to shipper'.lower() in msg.lower()):
					print "fucking returned"
					product.status='R'
					print product.shipping_cost
					product.return_cost=product.shipping_cost
					product.save()


				

				if ('Delivered'.lower() in msg.lower()):
					print "fucking delivered"
					product.status='C'
					product.save()

			product.tracking_data=json.dumps(tracking_data)
			product.save()

		except:#tracking number already exist
			print number 
			print "failed"	










# fedex shipment


	self.stdout.write("starting fedex api for fedex shipment")
	required_shipment = Shipment.objects.filter(Q(company='F')&(Q(status='P')|Q(status='DI')))
	#slug='aramex'
	str1=" FedEx"
	str2=" to FedEx"
	for shipment in required_shipment:
		print shipment.mapped_tracking_no
		number=shipment.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			tracker = easypost.Tracker.create(
				      tracking_code=number,
				      carrier="FEDEX"
				  )			#print data
		#print data


			for x in tracker['tracking_details']:
				time.sleep(1)
				msg=str(x['message'])
				date=str(x['datetime'])
				ur = dateutil.parser.parse(date)
				datestr= str(ur)[:-6]
				#print datestr
				date=datetime.datetime.strptime(datestr,format)
				date=date+ datetime.timedelta(hours=5,minutes=30)
				date=str(date)
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
				tracking_data.append({"status":msg,"date":date,"location":loc})	

				if ('delivered' in msg.lower()):
					print "fucking delivered"
					shipment.status='C'
					shipment.save()
					order=shipment.order
					#getting all shipments of that order	

					specific_shipments=Shipment.objects.filter(order=order)
					order_complete=True
					for specific_shipment in specific_shipments:
						if specific_shipment.status=='P':
							order_complete=False	

					if (order_complete):
						order.order_status='D'
						order.save()	
	

					break;	

			shipment.tracking_data=json.dumps(tracking_data)
			shipment.save()

		except:#tracking number already exist
			print number 
			print "failed"	



#Dtdc tracking

	self.stdout.write("starting Dtdc api for Dtdc product")
	required_product = Product.objects.filter(Q(company='DT')&(Q(status='P')|Q(status='DI'))).exclude(order__status='C')
	slug='dtdc'
	
	for product in required_product:
		print product.mapped_tracking_no
		number=product.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			y=api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data
		except:#tracking number already exist
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data


		for x in data['tracking']['checkpoints']:
			#print x['message']
			#print x['location']
			y1=str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0=remove_non_ascii_1(x['message'])
			str3=x['location'].encode('utf8')
			tracking_data.append({"status":str(str0),"date":str(str1),"location":str(str3)})
			if (str0=='DELIVERED'):
				print "fucking delivered"
				product.status='C'
				product.save()
				order=product.order
				#getting all products of that order

				specific_products=Product.objects.filter(order=order)
				order_complete=True
				for specific_product in specific_products:
					if specific_product.status=='P':
						order_complete=False

				if (order_complete):
					order.status='C'
					order.save()


				break;

		if (json.dumps(tracking_data)!='[]'):
			product.tracking_data=json.dumps(tracking_data)
			product.save()



	self.stdout.write("starting Aramex api for aramex shipment")
	required_shipment = Shipment.objects.filter(Q(company='DT')&(Q(status='P')|Q(status='DI')))
	slug='dtdc'
	
	for shipment in required_shipment:
		print shipment.mapped_tracking_no
		number=shipment.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			y=api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data
		except:#tracking number already exist
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data


		for x in data['tracking']['checkpoints']:
			#print x['message']
			#print x['location']
			y1=str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0=remove_non_ascii_1(x['message'])
			str3=x['location'].encode('utf8')
			tracking_data.append({"status":str(str0),"date":str(str1),"location":str(str3)})
			if (str0=='DELIVERED'):
				print "fucking delivered"
				shipment.status='C'
				shipment.save()
				myapp_order=shipment.order
				#getting all products of that order

				specific_shipments=Shipment.objects.filter(order=myapp_order)
				order_complete=True
				for specific_product in specific_shipments:
					if specific_product.status=='P':
						order_complete=False

				if (order_complete):
					myapp_order.order_status='D'
					myapp_order.save()


				break;

		if (json.dumps(tracking_data)!='[]'):
			shipment.tracking_data=json.dumps(tracking_data)
			shipment.save()


		#print tracking_data


	self.stdout.write("starting india Post api for india Post product")
	required_product = Product.objects.filter(Q(company='I')&(Q(status='P')|Q(status='DI'))).exclude(order__status='C')
	slug='india-post'
	
	for product in required_product:
		print product.mapped_tracking_no
		number=product.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			y=api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))

			time.sleep(0.5)
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data
		except:#tracking number already exist
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data

		print data

		for x in data['tracking']['checkpoints']:
			#print x['message']
			#print x['location']
			y1=str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0=remove_non_ascii_1(x['message'])
			str3=x['location'].encode('utf8')
			tracking_data.append({"status":str(str0),"date":str(str1),"location":str(str3)})
			if (str0=='Item Received'):
				print "fucking delivered"
				product.status='C'
				product.save()
				order=product.order
				#getting all products of that order

				specific_products=Product.objects.filter(order=order)
				order_complete=True
				for specific_product in specific_products:
					if specific_product.status=='P':
						order_complete=False

				if (order_complete):
					order.status='C'
					order.save()


				break;
		if (json.dumps(tracking_data)!='[]'):
			product.tracking_data=json.dumps(tracking_data)
			product.save()



	self.stdout.write("starting India Post api for India Post shipment")
	required_shipment = Shipment.objects.filter(Q(company='I')&(Q(status='P')|Q(status='DI')))
	slug='india-post'
	
	for shipment in required_shipment:
		print shipment.mapped_tracking_no
		number=shipment.mapped_tracking_no

		#to add tracking no
		tracking_data=[]

		try:
			y=api.trackings.post(tracking=dict(slug=slug, tracking_number=number, title="Title"))
			time.sleep(0.5)
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data
		except:#tracking number already exist
			data=api.trackings.get(slug, number, fields=['checkpoints'])
			#print data


		for x in data['tracking']['checkpoints']:
			#print x['message']
			#print x['location']
			y1=str(x['checkpoint_time'])
			str1 = y1.decode("windows-1252")
			str0=remove_non_ascii_1(x['message'])
			str3=x['location'].encode('utf8')
			tracking_data.append({"status":str(str0),"date":str(str1),"location":str(str3)})
			if (str0=='Item Received'):
				print "fucking delivered"
				shipment.status='C'
				shipment.save()
				myapp_order=shipment.order
				#getting all products of that order

				specific_shipments=Shipment.objects.filter(order=myapp_order)
				order_complete=True
				for specific_product in specific_shipments:
					if specific_product.status=='P':
						order_complete=False

				if (order_complete):
					myapp_order.order_status='D'
					myapp_order.save()


				break;

		if (json.dumps(tracking_data)!='[]'):
			product.tracking_data=json.dumps(tracking_data)
			product.save()
