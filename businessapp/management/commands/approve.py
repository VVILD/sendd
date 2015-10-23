from django.core.management.base import BaseCommand
from businessapp.models import Product, Order,AddressDetails
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

		today=date.today()
		yesterday = today - datetime.timedelta(days=1)

		end_max=datetime.datetime.combine(today, datetime.time(19, 00))
		start_min=datetime.datetime.combine(yesterday, datetime.time(19, 00))
		orders= Order.objects.filter(book_time__range=(start_min, end_max),status='P')
		qs = AddressDetails.objects.filter(Q(order=orders),~Q(status='Y')).distinct()
		print qs.count()
        qs.update(status='Y')
