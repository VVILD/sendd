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

class Command(BaseCommand):
  args = 'Arguments is not needed'
  help = 'Django admin custom command poc.'

  def handle(self, *args, **options):
      pass
