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
  	Product.objects.filter(~Q(kartrocket_order='') & Q(kartrocket_order__isnull=False) & (Q(mapped_tracking_no='') & Q(mapped_tracking_no__isnull=True) ))