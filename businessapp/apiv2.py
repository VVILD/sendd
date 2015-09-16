from django.db.models import Q
from tastypie.resources import ModelResource
from django.conf.urls import url
from tastypie.utils import trailing_slash
import time
from datetime import datetime, timedelta
from businessapp.models import *
from myapp.models import Zipcode, Shipment
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
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'A'):
                return True

            return bundle.obj.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

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
        authorization = Authorization()
        always_return_data = True

    def dehydrate(self, bundle):


        pk = bundle.data['resource_uri'].split('/')[4]

        try:
            business = Business.objects.get(pk=pk)
        except:
            bundle.data["msg"] = 'notregistered'
            return bundle

        try:
            bundle.data['manager'] = business.businessmanager.user.first_name + business.businessmanager.user.first_name
            bundle.data['manager_number'] = business.businessmanager.phone

        except:
            bundle.data['manager'] = 'Ankush Sharma'
            bundle.data['manager_number'] = '8080772210'

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
        if filters is None:
            filters = {}
        orm_filters = super(OrderResource, self).build_filters(filters)

        if 'q' in filters:
            orm_filters['q'] = filters['q']
        return orm_filters

    def apply_filters(self, request, orm_filters):
        base_object_list = super(OrderResource, self).apply_filters(request, {})
        if 'q' in orm_filters:
            return base_object_list.filter(business__username=orm_filters['q']).exclude(status='N')
        return base_object_list


    def hydrate(self, bundle):
        try:
            override_method = bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
        except:
            override_method = 'none'

        if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method == 'PATCH':
            print "i was here"
            return bundle

    def dehydrate(self, bundle):
        try:
            override_method = bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
        except:
            override_method = 'none'
        if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method == 'PATCH':
            print "i was here2"
            return bundle
        pk = bundle.data['resource_uri'].split('/')[4]
        products = Product.objects.filter(order__pk=pk)
        bundle.data['business'] = bundle.obj.business
        bundle.data['allowed_actual_tracking'] = bundle.obj.business.show_tracking_company
        bundle.data['products'] = [product.__dict__ for product in products]
        return bundle


class TrackingResource(CORSResource):
    class Meta:
        resource_name = 'tracking'
        authentication = Authentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<tracking_id>\w+)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('tracking'), name="api_tracking"),
        ]

    @csrf_exempt
    def tracking(self, request, tracking_id, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        master = False
        if not tracking_id:
            raise CustomBadRequest(
                code="request_invalid",
                message="No tracking_id found. Please supply tracking_id as a GET URL parameter")
        elif str(tracking_id).lower().startswith('m'):
            products = Product.objects.filter(order__master_tracking_number=tracking_id).values("real_tracking_no",
                                                                                                "tracking_data")
            master = True
        elif str(tracking_id).lower().startswith('se'):
            products = Product.objects.filter(barcode=tracking_id).values("real_tracking_no", "tracking_data")
        elif str(tracking_id).lower().startswith('b'):
            products = Product.objects.filter(real_tracking_no=tracking_id).values("real_tracking_no", "tracking_data")
        else:
            products = Shipment.objects.filter(real_tracking_no=tracking_id).values("real_tracking_no", "tracking_data")

        for product in products:
            product['tracking_data'] = json.loads(product['tracking_data'])
        bundle = {
            "master": master,
            "shipments": list(products)
        }
        self.log_throttled_access(request)
        return self.create_response(request, bundle)


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


class SearchResource(CORSResource):
    class Meta:
        resource_name = 'search'
        authentication = Authentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/tracking%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('tracking'), name="api_tracking"),
            url(r"^(?P<resource_name>%s)/business%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('business'), name="api_business"),
        ]

    def tracking(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        tracking_id = request.GET.get('tracking_id', False)

        if not tracking_id:
            raise CustomBadRequest(
                code="request_invalid",
                message="No tracking_id found. Please supply tracking_id as a GET parameter")
        elif str(tracking_id).startswith('SE') or str(tracking_id).startswith('se'):
            product = Product.objects.get(barcode=tracking_id)
        elif str(tracking_id).startswith('B'):
            product = Product.objects.get(real_tracking_no=tracking_id)
        else:
            product = Shipment.objects.get(real_tracking_no=tracking_id)

        bundle = {"order": product.order.__dict__}
        bundle['order']['products'] = [product.__dict__]

        self.log_throttled_access(request)
        return self.create_response(request, bundle)

    def business(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        business_username = request.GET.get('business', False)
        date = request.GET.get('date', False)
        start_date = datetime.strptime(str(date), "%d-%m-%Y")
        end_date = datetime.strptime(str(date), "%d-%m-%Y") + timedelta(days=1)
        if not business_username:
            raise CustomBadRequest(
                code="request_invalid",
                message="No business username found. Please supply business username as a GET parameter")
        if not date:
            raise CustomBadRequest(
                code="request_invalid",
                message="No date found. Please supply date as a GET parameter")
        orders = Order.objects.filter(business__username=business_username, book_time__gte=start_date,
                                      book_time__lt=end_date)
        result = []
        for order in orders:
            products = Product.objects.filter(order__pk=order.pk)
            order = order.__dict__
            order['products'] = [product.__dict__ for product in products]
            result.append(order)
        bundle = result
        self.log_throttled_access(request)
        return self.create_response(request, bundle)


class InvoiceResource(CORSResource):
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
        start_date = datetime.strptime(str(start_date), "%d-%m-%Y")
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
                    "remittance": product.remittance,
                    "tracking_id": product.real_tracking_no,
                    "quantity": product.quantity
                })
                orders[p_order]["total_shipping_cost"] += int(product.shipping_cost) + int(product.return_cost) + int(
                    product.cod_cost)
                if product.order.payment_method == 'C' and product.status != 'R':
                    orders[p_order]["total_cod_remittance"] += int(product.price)
                    if not product.remittance:
                        orders[p_order]["total_remittance_pending"] += int(product.price)
            else:
                orders[p_order] = {
                    "drop_address_address": product.order.address1 + product.order.address2,
                    "drop_address_pincode": product.order.pincode,
                    "drop_address_state": product.order.state,
                    "drop_address_city": product.order.city,
                    "receiver_name": product.order.name,
                    "total_shipping_cost": int(product.shipping_cost) + int(product.return_cost) + int(
                        product.cod_cost),
                    "total_cod_remittance": 0,
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
                                                   "remittance": product.remittance,
                                                   "tracking_id": product.real_tracking_no,
                                                   "quantity": product.quantity
                                               }]
                if product.order.payment_method == 'C' and product.status != 'R':
                    orders[p_order]["total_cod_remittance"] += int(product.price)
                    if not product.remittance:
                        orders[p_order]["total_remittance_pending"] += int(product.price)

        bundle = []
        for key, value in orders.iteritems():
            temp = [key, value]
            bundle.append(temp)
        bundle.sort(key=lambda x: int(x[0]))
        self.log_throttled_access(request)
        return self.create_response(request, bundle)


class BusinessBarcodeResource(ModelResource):
    class Meta:
        queryset = Business.objects.all()
        resource_name = 'business'
        authorization = Authorization()
        always_return_data = True


class BarcodeAllotmentResource(CORSModelResource):
    business = fields.ForeignKey(BusinessBarcodeResource, 'business', null=True)

    class Meta:
        resource_name = 'barcode_allotment'
        object_class = Barcode
        queryset = Barcode.objects.all()
        authorization = Authorization()
        authentication = Authentication()
        allowed_methods = ['post', 'patch', 'put', 'get']
        always_return_data = True
        filtering = {
            "value": ALL
        }

    def hydrate(self, bundle):

        try:
            business_obj = Business.objects.get(username=bundle.data['username'])
            bundle.data['business'] = "/bapi/v1/business/" + str(bundle.data['username']) + "/"
        except Business.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest("Username doesnt exist"))
        except KeyError:
            raise ImmediateHttpResponse(HttpBadRequest("Please Provide a valid username key"))

        return bundle

    def dehydrate(self, bundle):
        if bundle.request.method == 'PATCH':
            bundle.data['business'] = bundle.data['username']

        if bundle.request.method == 'GET':
            bundle.data['business'] = bundle.obj.business
            bundle.data['business_username'] = bundle.obj.business.username

        return bundle


class BarcodeFetchResource(CORSResource):
    class Meta:
        resource_name = 'barcode_fetch'
        authentication = Authentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('check_barcode'), name="api_check_barcode"),
        ]

    def check_barcode(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        barcode = request.GET.get('barcode', '')
        if not barcode:
            raise CustomBadRequest(
                code="request_invalid",
                message="No barcode found. Please supply barcode as a GET parameter")

        try:
            product = Product.objects.get(barcode=barcode)
            product_exists = True
        except ObjectDoesNotExist:
            product_exists = False

        try:
            barcode_assoc = Barcode.objects.get(value=barcode)
            barcode_associated = True
            business_username = barcode_assoc.business.username
            business_name = barcode_assoc.business.business_name
        except ObjectDoesNotExist:
            barcode_associated = False
            business_username = None
            business_name = None

        bundle = {
            "barcode_associated": barcode_associated,
            "product_exists": product_exists,
            "business_username": business_username,
            "business_name": business_name
        }
        self.log_throttled_access(request)
        return self.create_response(request, bundle)
