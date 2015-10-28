import datetime
from optparse import make_option
from concurrent import futures
from django.core.management import BaseCommand
import django_rq
from businessapp.models import Business, AddressDetails,Order
from datetime import date

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Assign default barcodes to the pickup address'

    option_list = BaseCommand.option_list + (
        make_option(
            "-w",
            "--workers",
            dest="workers",
            help="Number of workers",
            metavar="WRKS"
        ),
    )

    def order_saver(self, order, address):
        order.pickup_address=address
        order.save()
        return True

    def handle(self, *args, **options):
        if options['workers'] is None:
            workers = 1
        else:
            workers = int(options['workers'])
        businesses = Business.objects.all().select_related('addressdetails_set')
        for business in businesses:
            if business.assigned_pickup_time is not None:
                default_time=datetime.datetime.combine(date.today(), business.assigned_pickup_time)
            else:
                default_time=datetime.datetime.combine(date.today(), datetime.time(18, 00))

            if business.addressdetails_set.count() > 0:
                for address in business.addressdetails_set.all():
                    if address.default is True:
                        address.company_name = str(business.business_name) if business.business_name is not None else str(business.username),
                        address.contact_person = str(business.name) if business.name is not None else str(business.username),
                        address.phone_office = str(business.contact_office) if business.contact_office is not None else None,
                        address.phone_mobile = str(business.contact_mob) if business.contact_mob is not None else None,
                        address.address = str(business.address),
                        address.city = str(business.city),
                        address.state = str(business.state),
                        address.pincode = str(business.pincode),
                        # address.default_vehicle = 'B' if address.default_vehicle is None else address.default_vehicle,
                        address.default_pickup_time = default_time
                        address.warehouse = business.warehouse
                        address.save()
                        orders = Order.objects.filter(business=business)
                        with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                            futures_track = (executor.submit(self.order_saver, order, address) for order in orders)
                            for result in futures.as_completed(futures_track):
                                if result.exception() is not None:
                                    print('%s' % result.exception())
                                else:
                                    print(result.result())
            elif business.address and business.city and business.pincode and business.state:


                pickup_default = AddressDetails(
                    business = business,
                    company_name = str(business.business_name) if business.business_name is not None else str(business.username),
                    contact_person = str(business.name) if business.name is not None else str(business.username),
                    phone_office = str(business.contact_office) if business.contact_office is not None else None,
                    phone_mobile = str(business.contact_mob) if business.contact_mob is not None else None,
                    address = str(business.address),
                    default = True,
                    city = str(business.city),
                    state = str(business.state),
                    pincode = str(business.pincode),
                    # default_vehicle = 'B',
                    default_pickup_time = default_time,
                    warehouse=business.warehouse
                )
                pickup_default.save()
                print(pickup_default)

                orders = Order.objects.filter(business=business)
                with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                    futures_track = (executor.submit(self.order_saver, order, pickup_default) for order in orders)
                    for result in futures.as_completed(futures_track):
                        if result.exception() is not None:
                            print('%s' % result.exception())
                        else:
                            print(result.result())