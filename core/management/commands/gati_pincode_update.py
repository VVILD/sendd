import csv
from optparse import make_option
import os
from concurrent import futures
from django.core.management import BaseCommand, CommandError
from core.models import Pincode, StateCodes

__author__ = 'vatsalshah'


class Command(BaseCommand):
    help = 'Updates  servicable list from gati into our db'

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
        db_objs = Pincode.objects.filter(pincode=row['PINCODE'])
        if len(db_objs) > 0:
            count = 0
            pincode = None
            for obj in db_objs:
                obj.gati_servicable = True
                obj.save()
                pincode = obj.pincode
                count += 1
            if pincode is None:
                updated = False
            else:
                updated = True
            added = False
        else:
            state_code = "IN-" + row['STATE']
            state_name = str(StateCodes.objects.get(code=state_code).subdivision_name)
            new_obj = Pincode(
                pincode=row['PINCODE'],
                district_name=row['CITY'],
                state_name=state_name,
                gati_servicable=True
            )
            new_obj.save()
            updated = False
            added = True
            count = 1
            pincode = row['PINCODE']

        return {
            "pincode": pincode,
            "count": count,
            "added": added,
            "updated": updated
        }

    def handle(self, *args, **options):
        if options['path'] is None:
            raise CommandError("Please provide the csv file path")
        file_path = options['path']
        file_exists = os.path.exists(file_path)
        if not file_exists:
            raise CommandError("Path doesn't exist. Please provide a valid path")

        if options['workers'] is None:
            workers = 5
        else:
            workers = int(options['workers'])

        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            reader_list = [r for r in reader]

            with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures_track = (executor.submit(self.update_db, item) for item in reader_list)
                for result in futures.as_completed(futures_track):
                    if result.exception() is not None:
                        print('%s' % result.exception())
                    else:
                        print(result.result())
