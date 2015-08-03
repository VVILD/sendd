from django.db.models import Q
from tastypie.resources import ModelResource
from django.conf.urls import url
from tastypie.utils import trailing_slash
import time
from datetime import datetime, timedelta
from businessapp.models import *
from myapp.models import Zipcode
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.serializers import Serializer
from random import randint
import random
import urllib2, urllib
import hashlib, random
import os
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import ApiKeyAuthentication
import math
import string
from django.core.mail import send_mail
from push_notifications.models import APNSDevice, GCMDevice
import ast
import json
from tastypie.resources import Resource
from tastypie.fields import ListField

import urlparse
from tastypie.authentication import Authentication
from tastypie.http import HttpBadRequest
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from pickupboyapp.exceptions import CustomBadRequest


class urlencodeSerializer(Serializer):
    formats = ['json', 'jsonp', 'xml', 'yaml', 'html', 'plist', 'urlencode']
    content_types = {
        'json': 'application/json',
        'jsonp': 'text/javascript',
        'xml': 'application/xml',
        'yaml': 'text/yaml',
        'html': 'text/html',
        'plist': 'application/x-plist',
        'urlencode': 'application/x-www-form-urlencoded',
    }

    def from_urlencode(self, data, options=None):
        """ handles basic formencoded url posts """
        qs = dict((k, v if len(v) > 1 else v[0] )
                  for k, v in urlparse.parse_qs(data).iteritems())
        return qs

    def to_urlencode(self, content):
        pass


class OnlyAuthorization(Authorization):
    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        print "0kkkkkkkkkkkkkkkk"

        # these 2 lines due to product wanting to use this authorisation
        if (bundle.request.META["HTTP_AUTHORIZATION"] == 'A'):
            return True
        try:
            return bundle.request.META["HTTP_AUTHORIZATION"] == bundle.obj.business.apikey
        except:
            return False

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        print '1kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk'
        return object_list

    def create_detail(self, object_list, bundle):
        print '2kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk'
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []

        print "fgd"
        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        print "dfd"
        return bundle.request.META["HTTP_AUTHORIZATION"] == bundle.obj.business.apikey


    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


'''
Add CORS headers for tastypie APIs

Usage:
   class MyModelResource(CORSModelResource):
	   ...
	   
   class MyResource(CORSResource):
	   ...
	   
Authors:
   original source by http://codeispoetry.me/index.php/make-your-django-tastypie-api-cross-domain/
   extensions by @miraculixx
   * deal with ?format requests
   * always return CORS headers, even if always_return_data is False
   * handle exceptions properly (e.g. raise tastypie.BadRequests) 
   * provide two distinct classes for ModelResource and Resource classes
'''
from django.http.response import HttpResponse
from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import csrf_exempt
from tastypie.resources import Resource, ModelResource
import logging


class BaseCorsResource(Resource):
    """
	Class implementing CORS
	"""

    def error_response(self, *args, **kwargs):
        response = super(BaseCorsResource, self).error_response(*args, **kwargs)
        return self.add_cors_headers(response, expose_headers=True)

    def add_cors_headers(self, response, expose_headers=False):
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'content-type, authorization, x-requested-with, x-csrftoken'
        if expose_headers:
            response['Access-Control-Expose-Headers'] = 'Location'
        return response

    def create_response(self, *args, **kwargs):
        """
		Create the response for a resource. Note this will only
		be called on a GET, POST, PUT request if 
		always_return_data is True
		"""
        response = super(BaseCorsResource, self).create_response(*args, **kwargs)
        return self.add_cors_headers(response)

    def post_list(self, request, **kwargs):
        """
		In case of POST make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
        # logger.debug("post list %s\n%s" % (request, kwargs));
        response = super(BaseCorsResource, self).post_list(request, **kwargs)
        return self.add_cors_headers(response, True)

    def post_detail(self, request, **kwargs):
        """
		In case of POST make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
        # logger.debug("post detail %s\n%s" (request, **kwargs));
        response = super(BaseCorsResource, self).post_list(request, **kwargs)
        return self.add_cors_headers(response, True)

    def put_list(self, request, **kwargs):
        """
		In case of PUT make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
        response = super(BaseCorsResource, self).put_list(request, **kwargs)
        return self.add_cors_headers(response, True)

    def put_detail(self, request, **kwargs):
        response = super(BaseCorsResource, self).put_detail(request, **kwargs)
        return self.add_cors_headers(response, True)

    def method_check(self, request, allowed=None):
        """
		Check for an OPTIONS request. If so return the Allow- headers
		"""
        if allowed is None:
            allowed = []

        request_method = request.method.lower()
        allows = ','.join(map(lambda s: s.upper(), allowed))

        if request_method == 'options':
            response = HttpResponse(allows)
            response['Access-Control-Allow-Origin'] = '*'
            response[
                'Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken, X-HTTP-Method-Override'
            response['Access-Control-Allow-Methods'] = "POST"
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        if not request_method in allowed:
            response = http.HttpMethodNotAllowed(allows)
            response['Allow'] = allows
            raise ImmediateHttpResponse(response=response)

        return request_method

    def wrap_view(self, view):
        @csrf_exempt
        def wrapper(request, *args, **kwargs):
            request.format = kwargs.pop('format', None)
            wrapped_view = super(BaseCorsResource, self).wrap_view(view)
            return wrapped_view(request, *args, **kwargs)

        return wrapper


# Base Extended Abstract Model
class CORSModelResource(BaseCorsResource, ModelResource):
    pass


class CORSResource(BaseCorsResource, Resource):
    pass


class BusinessResource(CORSModelResource):
    class Meta:
        queryset = Business.objects.all()
        resource_name = 'business'
        # excludes = ['password']
        authorization = Authorization()
        always_return_data = True

    def dehydrate(self, bundle):


        pk = bundle.data['resource_uri'].split('/')[4]

        try:
            business = Business.objects.get(pk=pk)
        except:
            print "fuck"
            bundle.data["msg"] = 'notregistered'
            return bundle


        # pk=bundle.data['resource_uri'].split('/')[4]

        try:
            u = User.objects.get(username=business.businessmanager.username)
            bundle.data['manager'] = u.businessmanager.first_name
            bundle.data['manager_number'] = u.businessmanager.phone

        except:
            bundle.data['manager'] = 'Ankush Sharma'
            bundle.data['manager_number'] = '8080772210'
        # u = User.objects.get(username='ankit')
        # print u.businessmanager.phone
        return bundle


class OrderResource(CORSModelResource):
    business = fields.ForeignKey(BusinessResource, 'business', null=True)
    products = ListField(attribute='products', null=True)

    class Meta:
        queryset = Order.objects.all()
        resourcese_name = 'order'
        authorization = OnlyAuthorization()
        # authentication=Authentication()
        always_return_data = True
        ordering = ['book_time']


    def build_filters(self, filters=None):
        print "shit"
        print filters
        if filters is None:
            filters = {}
        orm_filters = super(OrderResource, self).build_filters(filters)

        if 'q' in filters:
            orm_filters['q'] = filters['q']
        return orm_filters

    def apply_filters(self, request, orm_filters):
        base_object_list = super(OrderResource, self).apply_filters(request, {})
        print orm_filters
        if 'q' in orm_filters:
            return base_object_list.filter(business__username=orm_filters['q']).exclude(status='N')
        print base_object_list
        return base_object_list


    def hydrate(self, bundle):
        try:
            override_method = bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
            print "changed to PATCH"
        except:
            override_method = 'none'
            print "hello"

        if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method == 'PATCH':
            print "patch"
            return bundle

    def dehydrate(self, bundle):
        try:
            pk = bundle.data['resource_uri'].split('/')[4]
            order = Order.objects.get(pk=pk)
            show_tracking_company = False
            if (order.business.show_tracking_company == 'Y'):
                show_tracking_company = True

            product = Product.objects.filter(order=order)
            print product
            l = []
            for p in product:
                product_name = p.name
                product_quantity = p.quantity
                print '1'
                product_weight = p.weight
                product_applied_weight = p.applied_weight
                product_price = p.price
                product_shipping_cost = p.shipping_cost
                product_sku = p.sku
                product_trackingid = p.real_tracking_no

                print '2'

                tracking_json = json.loads(p.tracking_data)
                print '3'
                product_status = tracking_json[-1]['status'].encode('ascii', 'ignore')
                product_date = tracking_json[-1]['date'].encode('ascii', 'ignore')
                product_location = tracking_json[-1]['location'].encode('ascii', 'ignore')
                print len(tracking_json)
                print "asd"
                raw_data = ' '
                try:
                    if (show_tracking_company):
                        raw_data = raw_data + str(p.mapped_tracking_no) + "&nbsp; &nbsp; &nbsp; "
                        if (p.company == "F"):
                            raw_data = raw_data + "FEDEX"
                        elif (p.company == "D"):
                            raw_data = raw_data + "DELHIVERY"
                        elif (p.company == "P"):
                            raw_data = raw_data + "Professional"
                        elif (p.company == "G"):
                            raw_data = raw_data + "gati"
                        elif (p.company == "A"):
                            raw_data = raw_data + "ARAMEX"
                        elif (p.company == "E"):
                            raw_data = raw_data + "Ecomexpress"
                        elif (p.company == "DT"):
                            raw_data = raw_data + "DTDC"
                        elif (p.company == "FF"):
                            raw_data = raw_data + "First Flight"
                        else:
                            raw_data = raw_data + "ERROR"

                        raw_data = raw_data + "<br>"


                except:
                    print "shit"

                for x in range(0, len(tracking_json)):
                    raw_data = raw_data + tracking_json[x]['status'].encode('ascii',
                                                                            'ignore') + "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;" + \
                               tracking_json[x]['date'].encode('ascii',
                                                               'ignore') + "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;" + \
                               tracking_json[x]['location'].encode('ascii', 'ignore') + "<br>"

                print raw_data
                print '3.5'
                l.append({"product_name": product_name, "product_quantity": product_quantity,
                          "product_weight": product_weight, "product_applied_weight": product_applied_weight,
                          "product_price": product_price, "product_shipping_cost": product_shipping_cost,
                          "product_status": raw_data, "product_date": product_date,
                          "product_location": product_location, "product_sku": product_sku,
                          "product_trackingid": product_trackingid, })
                print '4'
            data = json.dumps(l)

            # bundle.data['products']=data
            bundle.data['products'] = l

            bundle.data['status'] = order.status
            bundle.data['date'] = order.book_time.date()
        # bundle.data['time']=order.book_time.time()

        # bundle.data['order_no']=436+int(bundle.data['id'])
        # print bundle.data['order_no']
        except:
            print "shit"

        # bundle.data['ucts']=[{"product_date": "2015-06-07 18:40:20 ", "product_price": 50, "product_location": "Mumbai (Maharashtra)", "product_applied_weight": "null", "product_method": "Premium", "product_quantity": "null", "product_status": "Booking Received", "product_name": "clothes", "product_weight": 2, "product_shipping_cost": "null"}, {"product_date": "2015-06-07 18:40:20 ", "product_price": 60, "product_location": "Mumbai (Maharashtra)", "product_applied_weight": "null", "product_method": "Bulk", "product_quantity": "null", "product_status": "Booking Received", "product_name": "books", "product_weight": 7, "product_shipping_cost": "null"}]

        return bundle


class ProductResource2(ModelResource):
    order = fields.ForeignKey(OrderResource, 'order', null=True)

    class Meta:
        queryset = Product.objects.all()
        resource_name = 'product'
        authorization = Authorization()
        authentication = Authentication()
        always_return_data = True
        serializer = urlencodeSerializer()
        ordering = ['date']
        allowed_methods = ['post']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<real_tracking_no>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]


    def build_filters(self, filters=None):
        print "shit"
        print filters
        if filters is None:
            filters = {}
        orm_filters = super(ProductResource2, self).build_filters(filters)

        if 'q' in filters:
            orm_filters['q'] = filters['q']
        return orm_filters

    def apply_filters(self, request, orm_filters):
        base_object_list = super(ProductResource2, self).apply_filters(request, {})
        print orm_filters
        if 'q' in orm_filters:
            return base_object_list.filter(order__business__username=orm_filters['q'])
        print base_object_list
        return base_object_list

    def hydrate(self, bundle):
        try:
            override_method = bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
            print "changed to PATCH"
        except:
            override_method = 'none'
            print "hello"

        if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method != 'PATCH':
            print "hhhhhhhhhhhh"
            # r.publish("b2b", "message")

            try:
                business = Business.objects.get(pk=bundle.data['username'])
                bundle.data['business'] = "/bapi/v1/business/" + str(bundle.data['username']) + "/"
                print "user identified"
            except:
                # print "fuck"
                bundle.data['business'] = "/bapi/v1/business/0/"
                bundle.data["msg"] = 'notregistered'
                print "user not identified"
                return bundle

            try:
                if not bundle.data['reference_id']:
                    bundle.data['reference_id'] = None
            except:
                bundle.data['reference_id'] = None

            try:
                if not bundle.data['email']:
                    bundle.data['email'] = None
            except:
                bundle.data['email'] = None

            if len(bundle.data['phone']) is not 10:
                raise ImmediateHttpResponse(HttpBadRequest("Enter valid phone number = 10 digits"))



            # create order
            # curl --dump-header - -H "Content-Type: application/json" -X POST --data '{ "username": "newuser3", "name": "asd" , "phone":"8879006197","street_address":"office no 307, powai plaza","city":"mumbai","state":"maharashtra" ,"pincode":"400076","country":"india" , "payment_method":"F" ,"pname":"['clothes','books']","pprice":"['50','60']" ,"pweight":"['2','7']" }' http://127.0.0.1:8000/bapi/v1/order/
            try:
                order = Order.objects.create(business=business, name=bundle.data['customer_name'],
                                             phone=bundle.data['phone'], address1=bundle.data['address1'],
                                             address2=bundle.data['address2'], city=bundle.data['city'],
                                             state=bundle.data['state'], pincode=bundle.data['pincode'],
                                             country=bundle.data['country'],
                                             payment_method=bundle.data['payment_method'],
                                             reference_id=bundle.data['reference_id'], email=bundle.data['email'],
                                             method=bundle.data['shipping_method'])
                print "order created	"

            except:
                print "aaaaassssssssssssss"
                bundle.data['errormsg'] = 'error creating order'

            bundle.data['order'] = "/bapi/v1/order/" + str(order.pk) + "/"

            return bundle

        if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method == 'PATCH':
            print "patch ho rha hai"
            return bundle

    def dehydrate(self, bundle):


        temp = bundle.data['real_tracking_no']

        bundle = {}
        bundle['tracking_no'] = temp

        return bundle


class InvoiceResource(Resource):
    class Meta:
        resource_name = 'invoice'
        authentication = Authentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('invoice'), name="api_invoice"),
        ]

    def invoice(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        start_date = request.GET.get('start_date', False)
        end_date = request.GET.get('end_date', False)
        b_username = request.GET.get('b_username', False)

        if not (start_date and end_date and b_username):
            raise CustomBadRequest(
                code="request_invalid",
                message="Please supply all 3 GET parameters: start_date, end_date and b_username")

        business = Business.objects.get(pk=b_username)
        start_date = datetime.strptime(str(start_date), "%d-%m-%Y") + timedelta(days=-1)
        end_date = datetime.strptime(str(end_date), "%d-%m-%Y") + timedelta(days=1)

        products = Product.objects.filter(Q(order__business=business), Q(status='C') | Q(status='R'),
                                          Q(date__lt=end_date), Q(date__gt=start_date))
        orders = {}
        for product in products:
            p_order = str(product.order)
            if p_order in orders:
                orders[p_order]['products'].append({
                    "date": product.date,
                    "name": product.name,
                    "applied_weight": product.applied_weight,
                    "shipping_cost": product.shipping_cost,
                    "cod_cost": product.cod_cost,
                    "return_cost": product.return_cost,
                    "price": product.price,
                    "remittance": product.remittance
                })
                orders[p_order]["total_shipping_cost"] += int(product.shipping_cost) + int(product.return_cost)
                if product.order.payment_method == 'C':
                    orders[p_order]["total_cod"] += int(product.price)
                    if not product.remittance:
                        orders[p_order]["total_remittance_pending"] += int(product.price)
            else:
                orders[p_order] = {
                    "drop_address_city": product.order.city,
                    "receiver_name": product.order.name,
                    "total_shipping_cost": int(product.shipping_cost) + int(product.return_cost),
                    "total_cod": 0,
                    "total_remittance_pending": 0
                }
                orders[p_order]['products'] = [{
                                                   "date": product.date,
                                                   "name": product.name,
                                                   "applied_weight": product.applied_weight,
                                                   "shipping_cost": product.shipping_cost,
                                                   "cod_cost": product.cod_cost,
                                                   "return_cost": product.return_cost,
                                                   "price": product.price,
                                                   "remittance": product.remittance
                                               }]
                if product.order.payment_method == 'C':
                    orders[p_order]["total_cod"] += int(product.price)
                    if not product.remittance:
                        orders[p_order]["total_remittance_pending"] += int(product.price)
        bundle = {
            "orders": orders
        }
        self.log_throttled_access(request)
        return self.create_response(request, bundle)