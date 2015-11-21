import datetime
from optparse import make_option
from concurrent import futures
from django.core.management import BaseCommand
import django_rq
from businessapp.models import Business, AddressDetails,Order
from datetime import date

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'return all completed orders to not approved and removed temp_time' \
           'if temp_time < current then remove temp_time'


    def handle(self, *args, **options):

        import pytz
        ads=pytz.timezone('Asia/Kolkata')

        completed_pickups=AddressDetails.objects.filter(status='C')
        completed_pickups.update(status='N',temp_time=None)

        not_done_pickups=AddressDetails.objects.filter(temp_time__lt=datetime.datetime.now())
        not_done_pickups.update(temp_time=None)


        not_done_pickups2=AddressDetails.objects.filter(status__in=['Y','A'],default_pickup_time__lt=datetime.datetime.now(),temp_time=None)
        for p in not_done_pickups2:
            p.default_pickup_time=datetime.datetime.combine(date.today(), p.default_pickup_time.astimezone(ads).time())
            p.save()




