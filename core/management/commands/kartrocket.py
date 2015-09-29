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

        product_list=Product.objects.filter((~Q(kartrocket_order='')) & Q(kartrocket_order__isnull=False) & (Q(mapped_tracking_no='') | Q(mapped_tracking_no__isnull=True) ))

        for product in product_list:
            print product
            kartrocket_order=product.kartrocket_order
            link = "http://crazymindtechnologies.kartrocket.co/index.php?route=feed/web_api/orders&version=2&key=c20ad4d76fe97759aa27a0c99bff6710&order_id="+kartrocket_order
            f = urllib.urlopen(link)
            myfile = f.read()
            myfiles=json.loads(myfile)
            try:
                for detail in myfiles['orders'][0]['order_history']:
                    if detail['awb_code'] is not None:
                        awb=detail['awb_code']
                        courier=detail['courier'][0]
                        product.mapped_tracking_no=awb
                        product.company=courier
                        product.save()
            except:
                print "fail"



        shipment_list=Shipment.objects.filter((~Q(kartrocket_order='')) & Q(kartrocket_order__isnull=False) & (Q(mapped_tracking_no='') | Q(mapped_tracking_no__isnull=True) ))

        for shipment in shipment_list:
            kartrocket_order=shipment.kartrocket_order
            link = "http://crazymindtechnologies.kartrocket.co/index.php?route=feed/web_api/orders&version=2&key=c20ad4d76fe97759aa27a0c99bff6710&order_id="+kartrocket_order
            f = urllib.urlopen(link)
            myfile = f.read()
            myfiles=json.loads(myfile)
            try:
                for detail in myfiles['orders'][0]['order_history']:
                    if detail['awb_code'] is not None:
                        awb=detail['awb_code']
                        courier=detail['courier'][0]
                        shipment.mapped_tracking_no=awb
                        shipment.company=courier
                        shipment.save()
            except:
                print "fail"
