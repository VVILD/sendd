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

        pending=Product.objects.filter(remittance=False)
        complete=Product.objects.filter(remittance=True)

        print "pending count:",pending.count()
        print "complete count:",complete.count()

        c=complete.update(remittance_status='C')
        p=pending.update(remittance_status='P')

        print "pending count:",pending.count()
        print "complete count:",complete.count()