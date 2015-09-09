import csv
from optparse import make_option
import os
from concurrent import futures
from django.core.management import BaseCommand, CommandError
from core.models import Pincode

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Updates oda/opa and cod servicable list from fedex into our db'

    option_list = BaseCommand.option_list + (
        make_option(
            "-p",
            "--path",
            dest="path",
            help="csv file path",
            metavar="PTH"
        ),
    )

    option_list = option_list + (
        make_option(
            "-w",
            "--workers",
            dest="workers",
            help="Number of workers",
            metavar="WRKS"
        ),
    )

    @staticmethod
    def update_db(row):
        if row['ODA-OPA / Regular Classification (Dom +Intl)'] == 'Regular':
            is_oda = False
        else:
            is_oda = True
        if row['COD Serviceable (Domestic Only)'] == 'COD':
            cod_servicable = True
        else:
            cod_servicable = False
        db_objs = Pincode.objects.filter(pincode=row['Postal Code'])
        count = 0
        pincode = None
        for obj in db_objs:
            obj.fedex_oda_opa = is_oda
            obj.fedex_cod_service = cod_servicable
            obj.fedex_servicable = True
            obj.save()
            pincode = obj.pincode
            count += 1
        if pincode is None:
            updated = False
        else:
            updated = True
        return {
            "pincode": pincode,
            "count": count,
            "updated": updated,
            "is_oda": is_oda,
            "cod_servicable": cod_servicable
        }

    def handle(self, *args, **options):
        if options['path'] is None:
            raise CommandError("Please provide the csv file path")
        file_path = options['path']
        file_exists = os.path.exists(file_path)
        if not file_exists:
            CommandError("Path doesn't exist. Please provide a valid path")

        if options['workers'] is None:
            workers = 5
        else:
            workers = int(options['workers'])

        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)

            with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures_track = (executor.submit(self.update_db, item) for item in reader)
                for result in futures.as_completed(futures_track):
                    if result.exception() is not None:
                        print('%s' % result.exception())
                    else:
                        print(result.result())