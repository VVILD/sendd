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

	required_product = Product.objects.filter()

	for product in required_product:
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
			print order.pk
