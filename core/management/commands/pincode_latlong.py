from django.core.management import BaseCommand
from geopy.geocoders import googlev3
from core.models import Pincode

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Updates lat long for pincodes'

    def handle(self, *args, **options):
        geolocator = googlev3.GoogleV3(api_key="AIzaSyBEfEgATQeVkoKUnaB4O9rIdX2K2Bsh63o")
        pincodes = Pincode.objects.filter(region_name="Mumbai").exclude(latitude__isnull=False)
        print("Total pincodes", pincodes.count())
        for pincode in pincodes:
            location = geolocator.geocode("{}, India".format(pincode.pincode))
            # print(location.address)
            location_lat_long = (location.latitude, location.longitude)
            print(pincode.pincode, location_lat_long, location.address)
            pincode.latitude, pincode.longitude = location.latitude, location.longitude
            pincode.save()