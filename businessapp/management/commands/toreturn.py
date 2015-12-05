import csv
from optparse import make_option
import os

from datetime import date
from django.core.management import BaseCommand, CommandError

from businessapp.models import Order, Product


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
            raise CommandError("Please provide the list")
        file_path = options['path']
        #print file_path
        query= Product.objects.filter(order__in=file_path)
        for p in query:
            p.status='R'
            p.save()
