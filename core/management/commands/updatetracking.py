import ast
import logging
from optparse import make_option
import re
from django.core.management.base import BaseCommand
from businessapp.models import Product
from core.fedex.config import FedexConfig
from core.fedex.services.track_service import FedexTrackRequest
from myapp.models import Shipment
import aftership
from django.db.models import Q
from concurrent import futures
import datetime
from bs4 import BeautifulSoup
import urllib2
import json


class Command(BaseCommand):
    help = 'Updates tracking info for all the services'

    option_list = BaseCommand.option_list + (
        make_option(
            "-w",
            "--workers",
            dest="workers",
            help="Number of workers",
            metavar="WRKS"
        ),
    )

    company_map = {
        'B': 'bluedart',
        'A': 'aramex',
        'DT': 'dtdc',
        'I': 'india-post'
    }
    REMOVE_LIST = ["fedex", "to fedex"]
    remove_regex = remove = '|'.join(REMOVE_LIST)
    aftership_api = aftership.APIv4('c46ba2ea-5a3e-43c9-bda6-793365ec1ebb')
    FEDEX_CONFIG_INDIA = FedexConfig(key='jFdC6SAqFS9vz7gY',
                                     password='6bxCaeVdszjUo2iHw5R3tbrBu',
                                     account_number='677853204',
                                     meter_number='108284345',
                                     use_test_server=False)
    logging.basicConfig(level=logging.DEBUG)

    @staticmethod
    def remove_non_ascii_1(raw_text):
        return ''.join(i for i in raw_text if ord(i) < 128)
    

    #takes string object as param
    # return numbe of hours away from today
    @staticmethod
    def hours_gone(string_date):
        date_obj=datetime.datetime.strptime(string_date,"%Y-%m-%d %H:%M:%S")
        now=datetime.datetime.now()
        return (now-date_obj).total_seconds()//3600


    def fedex_track(self, tp):
        product, client_type = tp[0], tp[1]
        result = []
        # Set this to the INFO level to see the response from Fedex printed in stdout.
        # NOTE: TRACKING IS VERY ERRATIC ON THE TEST SERVERS. YOU MAY NEED TO USE
        # PRODUCTION KEYS/PASSWORDS/ACCOUNT #.
        # We're using the FedexConfig object from example_config.py in this dir.
        track = FedexTrackRequest(self.FEDEX_CONFIG_INDIA)
        if product.tracking_data:
            tracking_data = ast.literal_eval(product.tracking_data)
        else:
            tracking_data = []
        original_length = len(tracking_data)
        track.TrackPackageIdentifier.Type = 'TRACKING_NUMBER_OR_DOORTAG'
        track.TrackPackageIdentifier.Value = str(product.mapped_tracking_no)

        # Fires off the request, sets the 'response' attribute on the object.
        try:
            track.send_request()

            for match in track.response.TrackDetails:
                for event in match.Events:
                    if event.EventType == 'RS':
                        product.status = 'R'
                        product.return_cost = product.shipping_cost
                        product.save()
                    if event.EventType == 'DL':
                        product.status = 'C'
                        product.save()
                        order = product.order

                        if client_type == 'customer':
                            specific_products = Shipment.objects.filter(order=order)
                        else:
                            specific_products = Product.objects.filter(order=order)
                        order_complete = True
                        for specific_product in specific_products:
                            if specific_product.status == 'P':
                                order_complete = False

                        if order_complete:
                            if client_type == 'customer':
                                order.order_status = 'D'
                            else:
                                order.status = 'C'
                            order.save()
                    if original_length > 0:
                        if tracking_data[-1]['date'] != (event.Timestamp).strftime('%Y-%m-%d %H:%M:%S'):
                            if match.StatusCode == "DE":
                                event_desc = "Delivery Exception (" + event.EventDescription + ")"
                            else:
                                event_desc = event.EventDescription
                            regex = re.compile(r'\b('+self.remove_regex+r')\b', flags=re.IGNORECASE)
                            event_desc = regex.sub("", event_desc)
                            if 'City' in event.Address:
                                location = event.Address.City
                            else:
                                location = '--'
                            tracking_data.append({
                                "status": event_desc,
                                "date": (event.Timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                                "location": location
                            })
                            product.tracking_data = json.dumps(tracking_data)
                            product.save()
                            result = {
                                "company": 'fedex',
                                "tracking_no": product.mapped_tracking_no,
                                "updated": True,
                                "error": False
                            }
                        else:
                            hours=self.hours_gone(tracking_data[-1]['date'])
                            if (hours>12):
                                product.warning=True
                                print product.pk
                                print "warning ayi hai"
                                product.save()

                            result = {
                                "company": 'fedex',
                                "tracking_no": product.mapped_tracking_no,
                                "updated": False,
                                "error": False
                            }
                    else:
                        if match.StatusCode == "DE":
                            event_desc = "Delivery Exception (" + event.EventDescription + ")"
                        else:
                            event_desc = event.EventDescription
                        regex = re.compile(r'\b('+self.remove_regex+r')\b', flags=re.IGNORECASE)
                        event_desc = regex.sub("", event_desc)
                        if 'City' in event.Address:
                            location = event.Address.City
                        else:
                            location = '--'
                        tracking_data.append({
                            "status": event_desc,
                            "date": (event.Timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                            "location": location
                        })
                        product.tracking_data = json.dumps(tracking_data)
                        product.save()
                        result = {
                            "company": 'fedex',
                            "tracking_no": product.mapped_tracking_no,
                            "updated": True,
                            "error": False
                        }
        except Exception,e:
            result = {
                "company": 'fedex',
                "tracking_no": product.mapped_tracking_no,
                "updated": False,
                "error": str(e)
            }
        return result

    def aftership_track(self, tp):
        product, client_type = tp[0], tp[1]
        tracking_data = []
        company = self.company_map[product.company]
        try:
            self.aftership_api.trackings.post(
                tracking=dict(slug=company, tracking_number=product.mapped_tracking_no, title="Title"))
            data = self.aftership_api.trackings.get(company, product.mapped_tracking_no, fields=['checkpoints'])
        except:
            data = self.aftership_api.trackings.get(company, product.mapped_tracking_no, fields=['checkpoints'])

        if data:
            result = {
                "company": company,
                "tracking_no": product.mapped_tracking_no,
                "updated": True,
                "error": False
            }
        else:
            result = {
                "company": company,
                "tracking_no": product.mapped_tracking_no,
                "updated": False,
                "error": True
            }
        for x in data['tracking']['checkpoints']:
            y1 = str(x['checkpoint_time'])
            str1 = y1.decode("windows-1252")
            str0 = self.remove_non_ascii_1(x['message'])
            str3 = x['location'].encode('utf8')
            tracking_data.append({"status": str(str0), "date": str(str1), "location": str(str3)})

            if 'shipment returned back to shipper'.lower() in str0.lower():
                product.status = 'R'
                product.return_cost = product.shipping_cost
                product.save()

            if 'delivered' in str0.lower():
                product.status = 'C'
                product.save()
                order = product.order
                # getting all products of that order

                if client_type == 'customer':
                    specific_products = Shipment.objects.filter(order=order)
                else:
                    specific_products = Product.objects.filter(order=order)
                order_complete = True
                for specific_product in specific_products:
                    if specific_product.status == 'P':
                        order_complete = False

                if order_complete:
                    if client_type == 'customer':
                        order.order_status = 'D'
                    else:
                        order.status = 'C'
                    order.save()

                break

        if json.dumps(tracking_data) != '[]':
            product.tracking_data = json.dumps(tracking_data)
            product.save()
        return result




    def ecom_track(self,tp):
        product, client_type = tp[0], tp[1]
        company='Ecom'
        completed=False
        tracking_data=[]
        url='https://billing.ecomexpress.in/track_me/multipleawb_open/?awb='+str(product.mapped_tracking_no)+'&order&news_go=track+now'
        try:
            soup = BeautifulSoup(urllib2.urlopen(url).read())
            col = [i.string.encode('utf-8').strip().replace('\xc2\xa0\xc2\xa0\xc2\xa0', "") for i in soup('td') if i.string != None and i.parent.a == None]
            del col[0]

            data =[]
            date = []
            new_data = []
            exp_date = [] #This variable stores the ETA of packages
            s = 0
            a = 0
            b = 0
            c = 0

            while s < len(col): #This loop is used to split the date and location
                date.append(col[s].split(','))
                s += 2

            while a < len(date): #This adds all the items to the list
                data.append(date[a][0].strip()), data.append(date[a][1].strip()), data.append(col[b + 1])
                exp_date.append(date[a][0])
                b += 2
                a += 1

            while c < len(data):
                new_data.append({"status" : data[c + 2], "date" : data[c],"location": data[c + 1] })
                c += 3

            # new_tracking = sorted(new_data, key=lambda k: k["date"])
            tracking_data=new_data[::-1]

            # for row in new_tracking:
            #     tracking_data.append(row)
            #     if "delivered" in row["status"].lower():
            #         completed=True

            result = {
                "company": company,
                "tracking_no": product.mapped_tracking_no,
                "updated": True,
                "error": False
            }

        except:
            result = {
                "company": company,
                "tracking_no": product.mapped_tracking_no,
                "updated": False,
                "error": True
            }

        if json.dumps(tracking_data) != '[]':
            product.tracking_data = json.dumps(tracking_data)
            product.save()

        if (completed):
            product.status = 'C'
            product.save()
            order = product.order
            # getting all products of that order

            if client_type == 'customer':
                specific_products = Shipment.objects.filter(order=order)
            else:
                specific_products = Product.objects.filter(order=order)
            order_complete = True
            for specific_product in specific_products:
                if specific_product.status == 'P':
                    order_complete = False

            if order_complete:
                if client_type == 'customer':
                    order.order_status = 'D'
                else:
                    order.status = 'C'
                order.save()

        return result

#parser("https://billing.ecomexpress.in/track_me/multipleawb_open/?awb=122066652&order&news_go=track+now")



    def handle(self, *args, **options):

        ecom_track_queue = []
        # Track Bluedart shipments for businesses and customers
        business_shipments = Product.objects.filter(
            (Q(company='E')) & (
                Q(status='P') | Q(status='DI'))).exclude(Q(order__status='C')| Q(order__status='N'))

        for business_shipment in business_shipments:
            ecom_track_queue.append((business_shipment, 'business'))

        customer_shipments = Shipment.objects.filter(
            ( Q(company='E')) & (
                Q(status='P') | Q(status='DI'))).exclude( Q(order__order_status='N')| Q(order__order_status='D'))

        for customer_shipment in customer_shipments:
            ecom_track_queue.append((customer_shipment, 'customer'))


        aftership_track_queue = []
        # Track Bluedart shipments for businesses and customers
        business_shipments = Product.objects.filter(
            (Q(company='B') | Q(company='A') | Q(company='DT') | Q(company='I')) & (
                Q(status='P') | Q(status='DI'))).exclude(Q(order__status='C')| Q(order__status='N'))

        for business_shipment in business_shipments:
            aftership_track_queue.append((business_shipment, 'business'))

        customer_shipments = Shipment.objects.filter(
            (Q(company='B') | Q(company='A') | Q(company='DT') | Q(company='I')) & (
                Q(status='P') | Q(status='DI'))).exclude( Q(order__order_status='N')| Q(order__order_status='D'))

        for customer_shipment in customer_shipments:
            aftership_track_queue.append((customer_shipment, 'customer'))


        fedex_track_queue = []
        fedex_business_shipments = Product.objects.filter(Q(company='F') & (Q(status='P') | Q(status='DI'))).exclude(Q(order__status='C')| Q(order__status='N'))

        for fedex_business_shipment in fedex_business_shipments:
            fedex_track_queue.append((fedex_business_shipment, 'business'))

        fedex_customer_shipments = Shipment.objects.filter(Q(company='F') & (Q(status='P') | Q(status='DI'))).exclude( Q(order__order_status='N')| Q(order__order_status='D'))

        for fedex_customer_shipment in fedex_customer_shipments:
            fedex_track_queue.append((fedex_customer_shipment, 'customer'))

        if options['workers'] is None:
            workers = 1
        else:
            workers = int(options['workers'])

        if len(aftership_track_queue) > 0:
            with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures_track = (executor.submit(self.aftership_track, item) for item in aftership_track_queue)
                for result in futures.as_completed(futures_track):
                    if result.exception() is not None:
                        print('%s' % result.exception())
                    else:
                        print(result.result())

        if len(fedex_track_queue) > 0:
            with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures_track = (executor.submit(self.fedex_track, item) for item in fedex_track_queue)
                for result in futures.as_completed(futures_track):
                    if result.exception() is not None:
                        print('%s' % result.exception())
                    else:
                        print(result.result())

        if len(ecom_track_queue) > 0:
            with futures.ThreadPoolExecutor(max_workers=workers) as executor:
                futures_track = (executor.submit(self.ecom_track, item) for item in ecom_track_queue)
                for result in futures.as_completed(futures_track):
                    if result.exception() is not None:
                        print('%s' % result.exception())
                    else:
                        print(result.result())

