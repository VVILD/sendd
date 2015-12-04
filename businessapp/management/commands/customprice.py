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

        b_list=["adorn","ajmera","Alive","bodypower","bootwale","bottomline","dealwithus","DEARA","vipul_yadav","DEZAINS","divineinternational","dubaria","drishti","ecell","eureka_paints","feltfetish","flintstop","footballmerchandise","furtados_andheri","gandhisouvenirs","giftmania","gifteez","gogappa","manav","accessorywala","happygiftmart","happydolphine","Hazelighting","herbalremedy","hexatriangle","randeep","Indiacircus","inkspire","kiarajewelss","Khushiz","KPS","kuotient","Vishal","lejion_kitchen","Leonish","mdfoods","stickerbazaar","mmf","morefashion","muhenera","Origin","panoraa","pricebaba","Print2Gift","PRREMIA","reitindiabhiwandi","sushma","madhav","resonancecandles","resonancedombivili","rhea","Ayesha","rocketboxandheri","saiimpexbhiwandi","gipsy","shriram","sisterhoodofstyle","ankur","stutikanodia","surbhigrover","thehappystyle","thelabelcorp","theshoppersadda","topcolor","towelexpression","veetee","vertex","triman","visionmedia","zenotrading"]

        price=[20,40]
        price2=[8,12]

        for b in b_list:
            pricingquerset=Pricing2.objects.filter(business=b,type='N',weight__weight="11.0")
            for p in pricingquerset:
                p.override=True
                if p.zone.zone=='a':
                    p.price=price[0]*22
                    p.save()
                else:
                    p.price=price[1]*22
                    p.save()

            pricingquerset=Pricing2.objects.filter(business=b,type='B',weight__weight__lt="10.9")
            for p in pricingquerset:
                p.override=True
                if p.zone.zone=='a':
                    p.price=price2[0]*10
                    p.save()
                else:
                    p.price=price2[1]*10
                    p.save()

            pricingquerset=Pricing2.objects.filter(business=b,type='B',weight__weight="11")
            for p in pricingquerset:
                p.override=True
                if p.zone.zone=='a':
                    p.price=price2[0]*11
                    p.save()
                else:
                    p.price=price2[1]*11
                    p.save()
