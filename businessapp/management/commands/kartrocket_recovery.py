import csv
from optparse import make_option
import os
from django.core.management import BaseCommand, CommandError

from businessapp.models import Order, Product, Business

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Updates kartrocket data'

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
                business = Business.objects.get(business_name=row["Business Name"])
                company = None
                if row['courier'] == 'ECOMEXP':
                    company = 'E'
                elif row['courier'] == 'FEDEX':
                    company = 'F'
                payment_method = 'F'
                if row["payment_method"] == "cod":
                    payment_method = 'C'
                order = Order(
                    name=row["shipping_firstname"],
                    phone=row["shipping_mobile"],
                    # email=row["Receiver's Email"],
                    address1=row["shipping_address_1"],
                    address2=row["shipping_address_2"],
                    city=row["shipping_city"],
                    state=row["shipping_zone"],
                    pincode=row["shipping_postcode"],
                    country=row["shipping_country"],
                    payment_method=payment_method,
                    status='DI' if company else 'PU',
                    method='N',
                    # reference_id=row["reference_id"],
                    business=business
                )
                order.save()
                try:
                    product = Product(
                        name=row['product_name'],
                        price=float(row['product_price']),
                        quantity=int(row["product_quantity"]),
                        applied_weight=float(str(row["weight"]).replace("kg", "")),
                        mapped_tracking_no=row["awb_code"],
                        company=company,
                        # barcode=row['Barcode Number'],
                        order=order
                    )
                    product.save()
                    print("{} created".format(row['awb_code']))
                except Exception as e:
                    order.delete()
                    print(str(e))
                    print("{} couldn't be created".format(row['awb_code']))

