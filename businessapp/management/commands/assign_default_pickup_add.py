from django.core.management import BaseCommand
from businessapp.models import Business, AddressDetails

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Assign default barcodes to the pickup address'

    def handle(self, *args, **options):
        businesses = Business.objects.all()
        for business in businesses:
            pickup_default = AddressDetails(
                business = business,
                address = business.address,
                default = True,
                city = business.city,
                state = business.state,
                pincode = business.pincode
            )