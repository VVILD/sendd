__author__ = 'vatsalshah'

from geopy.geocoders import googlev3
from geopy.distance import vincenty

geolocator = googlev3.GoogleV3(api_key="AIzaSyBEfEgATQeVkoKUnaB4O9rIdX2K2Bsh63o")
location = geolocator.geocode("Classique Centre, Gundavali, Andheri East, Mumbai")
print(location.address)
location_lat_long = (location.latitude, location.longitude)
location2 = geolocator.geocode("BOX8 Marol Naka, Marol Maroshi Road, Andheri East, Mumbai")
print(location2.address)
location2_lat_long = (location2.latitude, location2.longitude)
print(vincenty(location_lat_long, location2_lat_long).kilometers)