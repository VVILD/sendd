from django.core.management.base import BaseCommand
from businessapp.models import Product,Business
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
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch

import requests
import urllib

easypost.api_key = 'UX9cFcEOVCEvw32QgFjXBg'


format='%Y-%m-%d %H:%M:%S'


def remove_non_ascii_1(text):
	return ''.join(i for i in text if ord(i)<128)


class Command(BaseCommand):
  args = 'Arguments is not needed'
  help = 'Django admin custom command poc.'
 
  def handle(self, *args, **options):
  	x=Business.objects.filter()

	for y in x:
		try:

		    address=urllib.quote_plus(str(y.address))  
		    phone=urllib.quote_plus(str(8879006197))
		    user_phone=urllib.quote_plus(str(y.contact_office)+str(y.contact_mob))
		    order_no=urllib.quote_plus(str(y.pk))
		    name=urllib.quote_plus(str(y.name))
		    msg0 = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
		    msga = str(phone)
		    msg1 = "&msg=Pickup+details+for+order+no%3A"+str(order_no)+".%0D%0AName%3A"+str(name)+"%2C+Address%3A"+str(address)+"%2C+Mobile+No%3A"+str(user_phone)+"&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&format=text"
		    query = ''.join([msg0, msga, msg1])
		    req = requests.get(query)
		    print y.username+",",req
		except:
			print "failed",y.username