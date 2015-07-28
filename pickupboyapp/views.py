import json
from django.shortcuts import render
from pickupboyapp.models import PBUser, PBLocations

__author__ = 'vatsalshah'


def pb_location_view(request):
    location_map = []
    pb_users = PBUser.objects.all()
    for pb_user in pb_users:
        pb_location = PBLocations.objects.filter(pbuser=pb_user).order_by('-updated_at')[0]
        if pb_location is not None:
            location_map.append([pb_user.name, pb_location.lat, pb_location.lon])
    location_map_json = json.dumps(location_map)
    return render(request, 'pb_location.html', {"location_map": location_map_json})