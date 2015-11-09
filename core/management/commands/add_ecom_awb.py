import csv
from optparse import make_option
import os
from django.core.management import BaseCommand, CommandError
from core.models import EcomAWB

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Adds ecom awb'

    option_list = BaseCommand.option_list + (
        make_option(
            "-p",
            "--path",
            dest="path",
            help="csv file path",
            metavar="PTH"
        ),
    )
    option_list = option_list + (make_option("-f", action="store_true", dest="prepaid"),)
    option_list = option_list + (make_option("-c", action="store_true", dest="cod"),)

    def handle(self, *args, **options):
        if options['path'] is None:
            raise CommandError("Please provide the csv file path")
        file_path = options['path']
        file_exists = os.path.exists(file_path)
        if not file_exists:
            raise CommandError("Path doesn't exist. Please provide a valid path")

        created_awbs = []

        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if options['prepaid']:
                    label_type = 'P'
                elif options['cod']:
                    label_type = 'C'
                else:
                    raise CommandError("Please provide label type")
                try:
                    awb = EcomAWB(
                        awb=row["Air waybill"],
                        label_type=label_type,
                    )
                    awb.save()
                    print("{} created".format(row["Air waybill"]))
                    created_awbs.append(awb)
                except Exception as e:
                    print(str(e))
                    print("{} couldn't be created".format(row["Air waybill"]))
                    print("Reversing all the creations...")
                    for obj in created_awbs:
                        obj.delete()
                    print("All created orders reversed due to error")

