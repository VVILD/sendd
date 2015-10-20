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

        b_list=["dealwithus","ecell","vedantaorganics","trident","toppersnotes"]

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



        b_list=["vedantaorganics","trident","dealwithus","ecell"]

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

        b_list=["toppersnotes"]

        price=[10,15]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='B')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight)
                    p.save()
                else:
                    p.price=price[1]*round(p.weight.weight)
                    p.save()


        b_list=["fortune_wwe"]

        price=[12.5,12.5]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='B')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight)
                    p.save()
                else:
                    p.price=price[1]*round(p.weight.weight)
                    p.save()

        b_list=["towelkingdom"]

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

        b_list=["towelkingdom"]

        price=[20,32,40]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='N')
            for p in pricingquerset:
                if p.zone.zone=='a':
                    p.price=price[0]*round(p.weight.weight)
                    p.save()
                elif p.zone.zone=='b':
                    p.price=price[1]*round(p.weight.weight)
                    p.save()
                else:
                    p.price=price[2]*round(p.weight.weight)
                    p.save()