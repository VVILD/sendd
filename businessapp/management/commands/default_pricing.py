from django.core.management.base import BaseCommand
from businessapp.models import Product, Order
from myapp.models import Shipment
import easypost
import aftership
api = aftership.APIv4('c46ba2ea-5a3e-43c9-bda6-793365ec1ebb')
import json
import time
import dateutil.parser
import datetime
import urllib
import requests
from datetime import date,timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags




class Command(BaseCommand):
	args = 'Arguments is not needed'
	help = 'Django admin custom command poc.'
	
	def handle(self, *args, **options):

		y=Pricing.objects.filter( (~Q(normal_zone_a_0 = 15))|(~Q(normal_zone_a_1 = 15))|(~Q(normal_zone_a_2 = 13))|
			(~Q(normal_zone_b_0 = 20))|(~Q(normal_zone_b_1 = 30))|(~Q(normal_zone_b_2 = 26))|
			(~Q(normal_zone_c_0 = 25))|(~Q(normal_zone_c_1 = 33))|(~Q(normal_zone_c_2 = 32))|
			(~Q(normal_zone_d_0 = 30))|(~Q(normal_zone_d_1 = 40))|(~Q(normal_zone_d_2 = 38))|
			(~Q(normal_zone_e_0 = 38))|(~Q(normal_zone_e_1 = 48))|(~Q(normal_zone_e_2 = 45))|
			(~Q(bulk_zone_a = 8))|(~Q(bulk_zone_b = 9.5))|(~Q(bulk_zone_c = 11))|(~Q(bulk_zone_d = 13))|(~Q(bulk_zone_e = 15))
		  )
      #y=Order.objects.filter()

      	for x in y:
      		print str(x.username) +"|" str(x.business_name)

      		
		