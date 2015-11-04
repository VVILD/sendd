import csv
from optparse import make_option
import os
from django.core.management import BaseCommand, CommandError

from businessapp.models import Order, Product, Business

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Updates  servicable list from ecom into our db'

    option_list = BaseCommand.option_list + (
        make_option(
            "-p",
            "--path",
            dest="path",
            help="csv file path",
            metavar="PTH"
        ),
    )

    def handle(self, *args, **options):
        if options['path'] is None:
            raise CommandError("Please provide the csv file path")
        file_path = options['path']
        file_exists = os.path.exists(file_path)
        if not file_exists:
            raise CommandError("Path doesn't exist. Please provide a valid path")

        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                business = Business.objects.get(pk="apple")
                awb = int(row['AWB']) if row['AWB'] != "#N/A" else None
                company = None
                if row['Shipping Company'] == 'ECOMEXP':
                    company = 'E'
                elif row['Shipping Company'] == 'FEDEX':
                    company = 'F'
                order = Order(
                    name=row["Receiver's Name"],
                    phone=row["Receiver's Contact"],
                    email=row["Receiver's Email"],
                    address1=row["Receiver's Address 1"],
                    address2=row["Receiver's Address 2"],
                    city=row["Destination City"],
                    state=row["Destination State"],
                    pincode=row["Destination PinCode"],
                    country=row["Destination Country"],
                    payment_method=row["payment_method"],
                    status='DI' if company else 'PU',
                    method=row["shipping_method"],
                    reference_id=row["reference_id"],
                    business=business
                )
                order.save()
                try:
                    product = Product(
                        name=row['Item Name'],
                        price=float(row['Item Price']),
                        quantity=1,
                        # applied_weight=0.30 if awb else None,
                        # mapped_tracking_no=str(awb),
                        company=company,
                        # barcode=row['Barcode Number'],
                        order=order
                    )
                    if awb:
                        product.mapped_tracking_no = str(awb)
                        product.applied_weight = 0.30
                    product.save()
                    print("{} created".format(row['AWB']))
                except Exception as e:
                    order.delete()
                    print(str(e))
                    print("{} couldn't be created".format(row['AWB']))

