import csv
from optparse import make_option
import os

from datetime import datetime
from django.core.management import BaseCommand, CommandError

from businessapp.models import Order


class Command(BaseCommand):
    help = 'Updates  servicable list from nandan into our db'

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

            mapped_orders = []
            for row in reader:
                try:
                    order = Order.objects.get(order_no=row["order_no"])
                    for product in order.product_set.all():
                        if "AWB NO" in row:
                            product.mapped_tracking_no = row["AWB NO"]
                            product.company = 'NA'
                        if 'STATUS' in row:
                            if row['STATUS'] == 'DELIVERED':
                                product.status = 'C'
                                if 'DELIVERY DATE' in row:
                                    try:
                                        delivery_time = datetime.strptime(row['DELIVERY DATE'], "%d/%m/%y")
                                        product.actual_delivery_timestamp = delivery_time
                                    except:
                                        pass
                            elif row['STATUS'] == 'Return':
                                product.status = 'R'
                        product.save()
                    mapped_orders.append(order)
                    print("awb {} mapped for order no {} of business {}".format(row["AWB NO"], order.order_no, order.business.business_name))
                except Exception as e:
                    print(str(e))
                    print("Reverting all previous orders...")
                    for obj in mapped_orders:
                        for p in obj.product_set.all():
                            p.mapped_tracking_no = None
                            p.company = None
                            p.save()
                    print("Revert completed. Please restart after resolving the errors")
