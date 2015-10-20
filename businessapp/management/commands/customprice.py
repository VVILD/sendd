from django.core.management.base import BaseCommand
from businessapp.models import *
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

        b_list=["DEARA","gogappa","KPS","laxmiprint"]

        price=[20,40]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='N')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight/0.5)
                    p.save()
                else:
                    p.price=price[1]*round(p.weight.weight/0.5)
                    p.save()

        b_list=["mdfoods","shreeji_group"]

        price=[20,45]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='N')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight/0.5)
                    p.save()
                else:
                    p.price=price[1]*round(p.weight.weight/0.5)
                    p.save()


        b_list=["zorooms"]

        price=[25,50]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='N')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight/0.5)
                    p.save()
                else:
                    p.price=price[1]*round(p.weight.weight/0.5)
                    p.save()


        b_list=["DEARA","gogappa","KPS","mdfoods"]

        price=[8,12]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='B')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight)
                    p.save()
                else:
                    p.price=price[1]*round(p.weight.weight)
                    p.save()

        b_list=["laxmiprint","shreeji_group"]

        price=[20,20]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='B')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight)
                    p.save()
                else:
                    p.price=price[1]*round(p.weight.weight)
                    p.save()


        b_list=["zorooms"]

        price=[10,14]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='B')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight)
                    p.save()
                else:
                    p.price=price[1]*round(p.weight.weight)
                    p.save()

