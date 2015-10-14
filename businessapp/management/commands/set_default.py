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


        ndict = {'a': [(0.25,15), (0.5,15), (1,28), (1.5,41),(2,54), (2.5,67), (3,80), (3.5,93), (4,106), (4.5,119), (5,132), (5.5,145),(6,158), (6.5,171), (7,184),(7.5,197), (8,210), (8.5,223), (9,236),(9.5,249), (10,262), (11,286)],
                 'b': [(0.25,20), (0.5,30), (1,56), (1.5,82),(2,108), (2.5,134), (3,160), (3.5,186),(4,212),(4.5,238), (5,264), (5.5,290),(6,316), (6.5,342),(7,368),(7.5,394), (8,420), (8.5,446),(9,472),(9.5,498), (10,524), (11,572)],
                 'c': [(0.25,25), (0.5,33), (1,65), (1.5,97),(2,129), (2.5,161), (3,193), (3.5,225),(4,257),(4.5,289), (5,321), (5.5,353),(6,385), (6.5,417),(7,449),(7.5,481), (8,513), (8.5,545),(9,577),(9.5,609), (10,641), (11,704)],
                 'd': [(0.25,30), (0.5,40), (1,78), (1.5,116),(2,154), (2.5,192), (3,230),(3.5,268), (4,306),(4.5,344), (5,382),(5.5,420), (6,458),(6.5,496), (7,534),(7.5,572), (8,610), (8.5,648),(9,686),(9.5,724), (10,762), (11,836)],
                 'e': [(0.25,38), (0.5,48), (1,93), (1.5,138),(2,183), (2.5,228), (3,273),(3.5,318), (4,363),(4.5,408), (5,453),(5.5,498), (6,543),(6.5,588), (7,633),(7.5,678), (8,723),(8.5,768), (9,813),(9.5,858), (10,903), (11,990)],
                 }

        bdict = {'a': [(1,80),(2,80), (3,80), (4,80), (5,80), (6,80), (7,80), (8,80), (9,80), (10,80) , (11,88)],
                 'b': [(1,95),(2,95), (3,95), (4,95), (5,95), (6,95), (7,95), (8,95), (9,95), (10,95) , (11,104.5)],
                 'c': [(1,110),(2,110), (3,110), (4,110), (5,110), (6,110), (7,110), (8,110), (9,110), (10,110), (11,121)],
                 'd': [(1,130),(2,130), (3,130), (4,130), (5,130), (6,130), (7,130), (8,130), (9,130), (10,130), (11,143)],
                 'e': [(1,150),(2,150), (3,150), (4,150), (5,150), (6,150), (7,150), (8,150), (9,150), (10,150), (11,165)]}

        y=Business.objects.all()
        for instance in y:
            for key in ndict:
                for w in ndict[key]:
                    zone = Zone.objects.get(zone=key)
                    weight = Weight.objects.get(weight=w[0])
                    print instance, weight , zone + "N"
                    p=Pricing2(business=instance,zone=zone,weight=weight,price=w[1],type='N')
                    p.save()

        for instance in y:
            for key in bdict:
                for w in bdict[key]:
                    zone = Zone.objects.get(zone=key)
                    weight = Weight.objects.get(weight=w[0])
                    print instance, weight , zone + "B"
                    p=Pricing2(business=instance,zone=zone,weight=weight,price=w[1],type='B')
                    p.save()
