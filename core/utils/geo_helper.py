from core.models import Pincode

__author__ = 'vatsalshah'

from geopy.geocoders import GeoNames, googlev3
from geopy.distance import vincenty

geolocator = googlev3.GoogleV3(api_key="AIzaSyBEfEgATQeVkoKUnaB4O9rIdX2K2Bsh63o")
# geolocator = GeoNames()
pincodes = Pincode.objects.filter(region_name="Mumbai")
for pincode in pincodes:
    location = geolocator.geocode("{}, India".format(pincode.pincode))
    # print(location.address)
    location_lat_long = (location.latitude, location.longitude)
    print(pincode.pincode, location_lat_long)
    pincode.latitude, pincode.longitude = location.latitude, location.longitude
    pincode.save()
# location2 = geolocator.geocode("BOX8 Marol Naka, Marol Maroshi Road, Andheri East, Mumbai")
# print(location2.address)
# location2_lat_long = (location2.latitude, location2.longitude)
# print(vincenty(location_lat_long, location2_lat_long).kilometers)