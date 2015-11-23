from django_project.celery import app
from geopy.distance import vincenty
from geopy.geocoders import googlev3


@app.task
def new_warehouse_reassignment(pk):
    from core.models import Warehouse, Pincode
    obj = Warehouse.objects.get(pk=pk)
    geolocator = googlev3.GoogleV3(api_key="AIzaSyBEfEgATQeVkoKUnaB4O9rIdX2K2Bsh63o")
    location = geolocator.geocode("{}, India".format(obj.pincode))
    obj.lat, obj.long = location.latitude, location.longitude
    obj.save()

    pincodes = Pincode.objects.filter(region_name=obj.city).exclude(latitude__isnull=True)
    warehouses = Warehouse.objects.filter(city=obj.city)

    from businessapp.models import Business
    businesses = Business.objects.filter(pincode__isnull=False).exclude(pincode=u'')

    for pincode in pincodes:
        closest_warehouse = None
        min_dist = 9999.9999
        for warehouse in warehouses:
            distance = vincenty((pincode.latitude, pincode.longitude), (warehouse.lat, warehouse.long)).kilometers
            if distance < min_dist:
                min_dist = distance
                closest_warehouse = warehouse
        pincode.warehouse = closest_warehouse
        pincode.save()

    for business in businesses:
        pincode_search = Pincode.objects.filter(pincode=str(business.pincode)).exclude(latitude__isnull=True, warehouse__isnull=True)
        if pincode_search.count() > 0:
            business.warehouse = pincode_search[0].warehouse
        else:
            business.warehouse = None
        business.save()

    print("Reassignment Complete for {}".format(obj.name))