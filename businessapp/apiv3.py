from django.conf.urls import url
from tastypie.utils import trailing_slash
import time
from datetime import datetime, timedelta

from businessapp.apiv4 import BusinessPickupAddressResource
from businessapp.models import *
from businessapp.tasks import send_business_labels
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
from tastypie.exceptions import Unauthorized, BadRequest
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
    def read_list(self, object_list, bundle):
        business_username = bundle.request.GET.get("username", None)
        if business_username is None:
            raise ImmediateHttpResponse(HttpBadRequest("Please Provide a valid username key"))
        try:
            business_obj = Business.objects.get(username=business_username)
        except Business.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest("Username doesnt exist"))
        try:
            if bundle.request.META["HTTP_AUTHORIZATION"] == 'B' or business_obj.apikey == bundle.request.META[
                "HTTP_AUTHORIZATION"]:
                return object_list.filter(business=business_obj)
            else:
                raise Unauthorized
        except KeyError:
            raise ImmediateHttpResponse(HttpBadRequest("Provide valid authorization headers"))

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?

        # these 2 lines due to product wanting to use this authorisation
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'B'):
                return True

            return bundle.obj.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'B'):
                return True

            return bundle.obj.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'B'):
                return True

            return bundle.obj.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

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

    def patch_list(self, request, **kwargs):
        response = super(BaseCorsResource, self).patch_list(request, **kwargs)
        return self.add_cors_headers(response, True)

    def patch_detail(self, request, **kwargs):
        response = super(BaseCorsResource, self).patch_detail(request, **kwargs)
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
            response['Access-Control-Allow-Methods'] = "POST, PATCH, PUT, GET"
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


class OrderResource3(CORSModelResource):
    business = fields.ForeignKey(BusinessResource, 'business', null=True)
    products = fields.ToManyField("businessapp.apiv3.ProductResource3", 'product_set', related_name='product')
    pickup_address = fields.ForeignKey(BusinessPickupAddressResource, 'pickup_address', null=True)

    class Meta:
        queryset = Order.objects.all()
        resource_name = 'order'
        authorization = OnlyAuthorization()
        authentication = Authentication()
        allowed_methods = ['post', 'patch', 'put', 'get']
        always_return_data = True
        ordering = ['book_time']
        filtering = {
            "reference_id": ALL,
            "book_time": ALL,
            "last_updated_status": ALL,
            "third_party_id": ALL
        }

    def hydrate(self, bundle):
        try:
            business_obj = Business.objects.get(username=bundle.data['username'])
            bundle.data['business'] = "/bapi/v1/business/" + str(bundle.data['username']) + "/"
            pickup_addr = AddressDetails.objects.filter(business=business_obj)
            if pickup_addr.count() == 0:
                raise ImmediateHttpResponse(HttpBadRequest("No pickupaddress found for the business"))
            bundle.data['pickup_address'] = "/bapi/v4/pickup_address/" + str(pickup_addr.first().pk) + "/"
        except Business.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest("Username doesnt exist"))
        except KeyError:
            raise ImmediateHttpResponse(HttpBadRequest("Please Provide a valid username key"))

        try:
            if len(bundle.data['phone']) is not 10:
                raise ImmediateHttpResponse(HttpBadRequest("Enter valid phone number = 10 digits"))
        except:
            raise ImmediateHttpResponse(HttpBadRequest("Enter valid phone number = 10 digits"))

        for product in bundle.data['products']:
            try:
                y = Product.objects.get(barcode=product['barcode'])
                raise ImmediateHttpResponse(HttpBadRequest("Barcode already exist. Please enter unique barcode"))
            except Product.DoesNotExist:
                pass
            except KeyError:
                pass

        return bundle


    def dehydrate(self, bundle):

        products = Product.objects.filter(order__pk=bundle.data['order_no']).values("real_tracking_no", "sku",
                                                                                    "weight",
                                                                                    "name", "quantity", "price",
                                                                                    "status", "barcode")

        new_bundle = {
            "order_no": bundle.data['order_no'],
            "reference_id": bundle.data['reference_id'],
            "third_party_id": bundle.data['third_party_id'],
            "master_tracking_no": bundle.data['master_tracking_number'],
            "is_confirmed": bundle.data['confirmed'],
            "products": list(products),
            "status": bundle.data['status']
        }
        return new_bundle


class OrderPatchResource(CORSModelResource):
    business = fields.ForeignKey(BusinessResource, 'business', null=True)
    products = fields.ToManyField("businessapp.apiv3.ProductResource3", 'product_set', related_name='product')
    skip = True

    class Meta:
        queryset = Order.objects.all()
        resource_name = 'order_update'
        authorization = OnlyAuthorization()
        authentication = Authentication()
        allowed_methods = ['patch']
        allowed_update_fields = ['confirmed', 'username']
        always_return_data = True

    def update_in_place(self, request, original_bundle, new_data):
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest(
                'Only update on %s allowed' % ', '.join(
                    self._meta.allowed_update_fields
                )
            )

        return super(OrderPatchResource, self).update_in_place(
            request, original_bundle, new_data
        )

    def hydrate(self, bundle):
        try:
            business_obj = Business.objects.get(username=bundle.data['username'])
            bundle.data['business'] = "/bapi/v1/business/" + str(bundle.data['username']) + "/"
        except Business.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest("Username doesnt exist"))
        except KeyError:
            raise ImmediateHttpResponse(HttpBadRequest("Please Provide a valid username key"))

        try:
            if len(bundle.data['phone']) is not 10:
                raise ImmediateHttpResponse(HttpBadRequest("Enter valid phone number = 10 digits"))
        except:
            raise ImmediateHttpResponse(HttpBadRequest("Enter valid phone number = 10 digits"))

        return bundle

    def dehydrate(self, bundle):
        if self.skip:
            self.skip = False
            return bundle

        products = Product.objects.filter(order__pk=bundle.data['order_no']).values("real_tracking_no", "sku",
                                                                                    "weight",
                                                                                    "name", "quantity", "price")

        new_bundle = {
            "order_no": bundle.data['order_no'],
            "reference_id": bundle.data['reference_id'],
            "third_party_id": bundle.data['third_party_id'],
            "master_tracking_no": bundle.data['master_tracking_number'],
            "is_confirmed": bundle.data['confirmed'],
            "products": list(products)
        }
        self.skip = True
        return new_bundle
        # return bundle


class OrderPatchReferenceResource(CORSModelResource):
    class Meta:
        resource_name = 'confirm_orders'
        authentication = Authentication()
        authorization = OnlyAuthorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('confirm_orders'), name="api_confirm_orders"),
        ]

    def confirm_orders(self, request, **kwargs):
        self.method_check(request, allowed=['patch'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if not request.body:
            raise CustomBadRequest("error", 'Please supply a valid json in the format {"update":["ID1", "ID2", "ID3"]}')

        try:
            update_ids = json.loads(request.body)
        except:
            raise CustomBadRequest("error", 'Please supply a valid json in the format {"update":["ID1", "ID2", "ID3"]}')

        if not 'update' in update_ids:
            raise CustomBadRequest("error", 'Please supply a valid json in the format {"update":["ID1", "ID2", "ID3"]}')

        if not 'username' in update_ids:
            raise CustomBadRequest("error", 'Please supply a username')

        try:
            business_obj = Business.objects.get(username=update_ids['username'])
        except Business.DoesNotExist:
            raise CustomBadRequest("error", "Username doesn't exist")
        except KeyError:
            raise CustomBadRequest("error", 'Please supply a valid username')

        db_objs = Order.objects.filter(third_party_id__in=update_ids['update'], business=business_obj)
        updated_orders = []
        for db_obj in db_objs:
            db_obj.confirmed = True
            db_obj.save()
            products = Product.objects.filter(order__pk=db_obj.order_no).values("real_tracking_no", "sku",
                                                                                "weight",
                                                                                "name", "quantity", "price")
            updated_orders.append({
                "order_no": db_obj.order_no,
                "reference_id": db_obj.reference_id,
                "third_party_id": db_obj.third_party_id,
                "master_tracking_no": db_obj.master_tracking_number,
                "is_confirmed": db_obj.confirmed,
                "products": list(products)
            })

        bundle = {"updated_orders": updated_orders}

        self.log_throttled_access(request)
        return self.create_response(request, bundle)


class EmailLabelsResource(CORSModelResource):
    class Meta:
        resource_name = 'email_labels'
        authentication = Authentication()
        authorization = OnlyAuthorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('email_labels'), name="api_email_labels"),
        ]

    def email_labels(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)

        if not request.body:
            raise CustomBadRequest("error",
                                   'Please supply a valid json in the format {"third_party_ids":["ID1", "ID2", "ID3"]}')

        third_party_ids = self.deserialize(request, request.body)

        if not 'third_party_ids' in third_party_ids:
            raise CustomBadRequest("error",
                                   'Please supply a valid json in the format {"third_party_ids":["ID1", "ID2", "ID3"]}')
        if type(third_party_ids['third_party_ids']) is not list:
            raise CustomBadRequest("error",
                                   'Please supply a valid json in the format {"third_party_ids":["ID1", "ID2", "ID3"]}')

        if not 'username' in third_party_ids:
            raise CustomBadRequest("error", 'Please supply a username')

        try:
            business_obj = Business.objects.get(username=third_party_ids['username'])
        except Business.DoesNotExist:
            raise CustomBadRequest("error", "Username doesn't exist")
        except KeyError:
            raise CustomBadRequest("error", 'Please supply a valid username')

        db_objs = Order.objects.filter(third_party_id__in=third_party_ids['third_party_ids'], business=business_obj)
        if db_objs.count() == 0:
            return self.create_response(request, {"success": False, "message": "No labels to create"})

        send_business_labels.delay(db_objs, business_obj)

        self.log_throttled_access(request)
        return self.create_response(request, {"success": True, "message": "Labels created"})


class ProductResource3(ModelResource):
    order = fields.ToOneField(OrderResource3, 'order')

    class Meta:
        queryset = Product.objects.all()
        resource_name = 'product'
        authorization = Authorization()
        authentication = Authentication()
        always_return_data = True


class ShippingEstimateResource(CORSResource):
    class Meta:
        resource_name = 'shipping_estimate'
        authentication = Authentication()
        authorization = OnlyAuthorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_estimate'), name="api_get_estimate"),
        ]

    def get_estimate(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        method = request.GET.get('shipping_method', None)
        payment_method = request.GET.get('payment_method', None)
        item_price = request.GET.get('item_price', None)
        item_weight = request.GET.get('item_weight', None)
        delivery_pincode = request.GET.get('delivery_pincode', None)
        business_username = request.GET.get('business_username', None)
        if not all(x is not None for x in
                   (method, payment_method, item_price, item_weight, delivery_pincode, business_username)):
            raise CustomBadRequest("error", "Missing parameter")
        lbh = request.GET.get('lbh', None)
        item_price = float(item_price)
        item_weight = float(item_weight)

        if (payment_method == 'C'):
            cod_price1 = (1.5 / 100) * item_price
            if (cod_price1 < 40):
                cod_price = 40
            else:
                cod_price = cod_price1

        else:
            cod_price = 0

        pincode = delivery_pincode
        print pincode

        two_digits = pincode[:2]
        three_digits = pincode[:3]

        try:
            pricing = Pricing.objects.get(business__username=business_username)
        except:
            raise CustomBadRequest("error", "Business Username incorrect/Pricing for business not set")

        if (method == 'N'):
            if (three_digits == '400'):
                price1 = pricing.normal_zone_a_0
                price2 = pricing.normal_zone_a_1
                price3 = pricing.normal_zone_a_2

            elif (
                                                        two_digits == '41' or two_digits == '42' or two_digits == '43' or two_digits == '44' or three_digits == '403' or two_digits == '36' or two_digits == '37' or two_digits == '38' or two_digits == '39'):
                price1 = pricing.normal_zone_b_0
                price2 = pricing.normal_zone_b_1
                price3 = pricing.normal_zone_b_2
            elif (two_digits == '56' or two_digits == '11' or three_digits == '600' or three_digits == '700'):
                price1 = pricing.normal_zone_c_0
                price2 = pricing.normal_zone_c_1
                price3 = pricing.normal_zone_c_2

            elif (two_digits == '78' or two_digits == '79' or two_digits == '18' or two_digits == '19'):
                price1 = pricing.normal_zone_e_0
                price2 = pricing.normal_zone_e_1
                price3 = pricing.normal_zone_e_2
            else:
                price1 = pricing.normal_zone_d_0
                price2 = pricing.normal_zone_d_1
                price3 = pricing.normal_zone_d_2

            if item_weight <= 0.25:
                price = price1
            elif item_weight <= 0.50:
                price = price2
            else:
                price = price2 + math.ceil((item_weight * 2 - 1)) * price3

        if (method == 'B'):
            if (three_digits == '400'):
                price1 = pricing.bulk_zone_a

            elif (
                                                        two_digits == '41' or two_digits == '42' or two_digits == '43' or two_digits == '44' or three_digits == '403' or two_digits == '36' or two_digits == '37' or two_digits == '38' or two_digits == '39'):
                price1 = pricing.bulk_zone_b
            elif (two_digits == '56' or two_digits == '11' or three_digits == '600' or three_digits == '700'):
                price1 = pricing.bulk_zone_c

            elif (two_digits == '78' or two_digits == '79' or two_digits == '18' or two_digits == '19'):
                price1 = pricing.bulk_zone_e
            else:
                price1 = pricing.bulk_zone_d

            if (item_weight <= 10):
                price = price1 * 10
            else:
                price = price1 * item_weight

        price = math.ceil(1.20 * price)

        bundle = {
            "estimated_shipping_cost": price,
            "estimated_cod_cost": cod_price
        }
        self.log_throttled_access(request)
        return self.create_response(request, bundle)


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

        if not tracking_id:
            raise CustomBadRequest(
                code="request_invalid",
                message="No tracking_id found. Please supply tracking_id as a GET URL parameter")
        elif str(tracking_id).startswith('SE') or str(tracking_id).startswith('se'):
            product = Product.objects.get(barcode=tracking_id)
        elif str(tracking_id).startswith('B'):
            product = Product.objects.get(real_tracking_no=tracking_id)
        else:
            product = Shipment.objects.get(real_tracking_no=tracking_id)

        bundle = {"tracking_data": product.tracking_data}
        self.log_throttled_access(request)
        return self.create_response(request, bundle)


class BusinessPatchResource(CORSModelResource):
    class Meta:
        resource_name = 'business_patch'
        object_class = Business
        queryset = Business.objects.all()
        authorization = Authorization()
        authentication = Authentication()
        allowed_methods = ['patch']
        allowed_update_fields = ['is_completed']
        # always_return_data = True

    def update_in_place(self, request, original_bundle, new_data):
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest(
                'Only update on %s allowed' % ', '.join(
                    self._meta.allowed_update_fields
                )
            )

        return super(BusinessPatchResource, self).update_in_place(
            request, original_bundle, new_data
        )



class OrderCancelResource(CORSModelResource):
    products = fields.ToManyField("businessapp.apiv3.ProductResource3", 'product_set', related_name='product')
    skip = True

    class Meta:
        queryset = Order.objects.all()
        resource_name = 'order_cancel'
        authorization = OnlyAuthorization()
        authentication = Authentication()
        allowed_methods = ['patch']
        allowed_update_fields = ['status', 'username']
        always_return_data = True

    def update_in_place(self, request, original_bundle, new_data):
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest(
                'Only update on %s allowed' % ', '.join(
                    self._meta.allowed_update_fields
                )
            )

        if 'status' in new_data:
            products = Product.objects.filter(order__pk=original_bundle.data['order_no'])
            if new_data['status'] == 'N':
                products.update(status='CA')

        return super(OrderCancelResource, self).update_in_place(
            request, original_bundle, new_data
        )


    def dehydrate(self, bundle):
        if self.skip:
            self.skip = False
            return bundle

        products = Product.objects.filter(order__pk=bundle.data['order_no']).values("real_tracking_no", "sku",
                                                                                    "weight",
                                                                                    "name", "quantity", "price",
                                                                                    "status")

        new_bundle = {
            "order_no": bundle.data['order_no'],
            "products": list(products)
        }
        self.skip = True
        return new_bundle


class PincodecheckResource3(CORSResource):
    class Meta:
        resource_name = 'pending_orders'
        authentication = Authentication()
        authorization = Authorization()

    def hydrate(self, bundle):

        try:
            zipcode = Zipcode.objects.get(pincode=bundle.data['pincode'])
            bundle.data['valid'] = 1
        except:
            bundle.data['valid'] = 0
            bundle.data['msg'] = 'we dont have pickup service available in your desired pickup location.'

        return bundle


class PincodecheckResource(CORSResource):

    class Meta:
        resource_name = 'check_pincode'
        authentication = Authentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('check_pincode'), name="api_pending_orders"),
        ]

    def check_pincode(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        zipcode = request.GET.get('pincode', None)
        if not zipcode:
            raise CustomBadRequest(
                code="request_invalid",
                message="No pincode found. Please supply pincode as a GET parameter")

        pincode = Pincode.objects.filter(pincode=zipcode)
        if pincode.count() < 1:
            raise CustomBadRequest("request_invalid", "No pincode found")

        pincode_obj = pincode.first()
        if pincode_obj.region_name == 'Mumbai':
            valid = True
        else:
            valid = False
        bundle = {"valid": valid}
        self.log_throttled_access(request)
        return self.create_response(request, bundle)