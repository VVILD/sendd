import datetime
from django.core.management import BaseCommand
from businessapp.models import Business, AddressDetails
from datetime import date

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Assign default barcodes to the pickup address'

    def handle(self, *args, **options):
        businesses = Business.objects.all().select_related('addressdetails_set')
        for business in businesses:
            if business.addressdetails_set.count() > 0:
                for address in business.addressdetails_set.all():
                    if address.default is True:
                        address.company_name = business.business_name if business.business_name is not None else business.username,
                        address.contact_person = business.name if business.name is not None else business.username,
                        address.phone_office = business.contact_office if business.contact_office is not None else None,
                        address.phone_mobile = business.contact_mob if business.contact_mob is not None else None,
                        address.address = business.address,
                        address.city = business.city,
                        address.state = business.state,
                        address.pincode = business.pincode,
                        address.default_vehicle = 'B' if address.default_vehicle is None else address.default_vehicle,
                        address.default_pickup_time = business.assigned_pickup_time if business.assigned_pickup_time is not None else datetime.time(hour=18, minute=0, second=0)
                        address.save()
            elif business.address and business.city and business.pincode and business.state:

                if business.assigned_pickup_time:
                    default_time=datetime.datetime.combine(date.today(),business.assigned_pickup_time)
                else:
                    default_time=datetime.datetime.combine(date.today(),datetime.time(18, 00))

                pickup_default = AddressDetails(
                    business = business,
                    company_name = business.business_name if business.business_name is not None else business.username,
                    contact_person = business.name if business.name is not None else business.username,
                    phone_office = business.contact_office if business.contact_office is not None else None,
                    phone_mobile = business.contact_mob if business.contact_mob is not None else None,
                    address = business.address,
                    default = True,
                    city = business.city,
                    state = business.state,
                    pincode = business.pincode,
                    default_vehicle = 'B',
                    default_pickup_time = default_time
                )
                pickup_default.save()
                print(pickup_default)