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
	
	self.stdout.write("starting Aramex api for aramex product")
	required_product = Product.objects.filter(company='I',status='P')
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
		if (json.dumps(tracking_data)!='[]'):
			product.tracking_data=json.dumps(tracking_data)
			product.save()