import csv
from optparse import make_option
import os

from datetime import date
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
        #print file_path
        file_exists = os.path.exists(file_path)
        if not file_exists:
            raise CommandError("Path doesn't exist. Please provide a valid path")

        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            print "hi"
            mapped_orders = []
            for row in reader:
                print"hi1"
                try:
                    order = Order.objects.get(business='souled_store',name=row["name"],book_time__gt=date(2015, 11, 28))
                    print "adding reference id"
                    order.reference_id=row["ref"]
                    order.save()
                    if order.product_set.all().count()==1:
                        print "1 product only , adding barcode"
                        pro=order.product_set.first()
                        pro.barcode=row["barcode"]
                        pro.save()
                    else:
                        print "multiple products, cant do shit, reference_id is ",row["ref"]
                except Exception as e:
                    print(str(e))

                    print("order not found ",row["ref"])
