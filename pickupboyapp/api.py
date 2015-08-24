import datetime
import json
from random import randint
import urllib2

from django.conf.urls import url
from django.core import serializers
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.resources import Resource, QUERY_TERMS, ModelResource
from tastypie.utils import trailing_slash

from pickupboyapp.exceptions import CustomBadRequest
from myapp.models import Shipment, Namemail, Address
from myapp.models import Order as CustomerOrder
from businessapp.models import Order as BusinessOrder
from businessapp.models import Product, Business
from .models import PBLocations, PBUser


__author__ = 'vatsalshah'

time_map = {
    'M': (datetime.time(hour=10, minute=0, second=0), "10:00 - 12:00"),
    'A': (datetime.time(hour=14, minute=0, second=0), "13:00 - 15:00"),
    'E': (datetime.time(hour=14, minute=0, second=0), "16:00 - 18:00")
}


class PBUserResource(ModelResource):
    class Meta:
        resource_name = 'pb_users'
        object_class = PBUser
        queryset = PBUser.objects.all()
        allowed_methods = ['get']
        authorization = Authorization()

    def dehydrate(self, bundle):
        if bundle.request.method == 'GET':
            bundle.data['otp'] = randint(1000, 9999)
            msg0 = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
            msga = str(bundle.data['phone'])
            msg1 = "&msg=Welcome+to+Sendd.+Your+OTP+is+"
            msg2 = str(bundle.data['otp'])
            msg3 = ".This+message+is+for+automated+verification+purpose.+No+action+required.&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&v=1.1&format=text"
            # url1="http://49.50.69.90//api/smsapi.aspx?username=doormint&password=naman123&to="+ str(bundle.data['phone']) +"&from=DORMNT&message="
            query = ''.join([msg0, msga, msg1, msg2, msg3])
            urllib2.urlopen(query).read()
        return bundle


class PBLocationsResource(ModelResource):
    pbuser = fields.ForeignKey(PBUserResource, 'pbuser', full=True)

    class Meta:
        resource_name = 'pb_locations'
        object_class = PBLocations
        queryset = PBLocations.objects.all()
        allowed_methods = ['get', 'post', 'delete', 'put']
        authorization = Authorization()
        filtering = {
            'updated_at': QUERY_TERMS,
            'pbuser': QUERY_TERMS
        }


class PickupboyResource(Resource):
    class Meta:
        resource_name = 'pending_orders'
        authentication = Authentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('pending_orders'), name="api_pending_orders"),
        ]

    def pending_orders(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        pb_ph = request.GET.get('pb_ph', '')
        if not pb_ph:
            raise CustomBadRequest(
                code="request_invalid",
                message="No pickupboy found. Please supply pb_ph as a GET parameter")
        result = []
        customer_pending_orders = CustomerOrder.objects.filter(pb__phone=pb_ph, order_status='A',
                                                               date=datetime.date.today()).order_by("time")
        business_pending_orders = BusinessOrder.objects.filter(business__pb__phone=pb_ph, status='P')

        for order in business_pending_orders:
            business = Business.objects.get(pk=order.business.pk)
            shipments = []
            for product in Product.objects.filter(order=order, status='P').all():
                shipments.append({
                    "name": product.name,
                    "quantity": product.quantity,
                    "sku": product.sku,
                    "price": product.price,
                    "weight": product.weight,
                    "real_tracking_no": product.real_tracking_no,
                    "company": product.company,
                    "shipping_cost": product.shipping_cost,
                    "barcode": product.barcode
                })
            order_transformed = {
                "b_business_name": business.business_name,
                "b_username": business.username,
                "b_address": business.address,
                "b_contact_mob": business.contact_mob,
                "b_contact_office": business.contact_office,
                "b_name": business.name,
                "pickup_time": business.assigned_pickup_time,
                "b_pincode": business.pincode,
                "b_city": business.city,
                "b_state": business.state,
                "address1": order.address1,
                "address2": order.address2,
                "name": order.name,
                "phone": order.phone,
                "pincode": order.pincode,
                "order_id": order.pk,
            }
            detailed_order = {
                "type": "b2b",
                "order": order_transformed,
                "shipments": shipments
            }
            if len(detailed_order['shipments']) > 0:
                result.append(detailed_order)

        for order in customer_pending_orders:
            shipments = []
            for shipment in Shipment.objects.filter(order=order, status='P'):
                # drop_address = Address.objects.filter(pk=shipment.drop_address.pk)
                drop_address = None
                if shipment.drop_address is not None:
                    drop_address = {
                        "drop_address_flat_no": shipment.drop_address.flat_no,
                        "drop_address_locality": shipment.drop_address.locality,
                        "drop_address_city": shipment.drop_address.city,
                        "drop_address_state": shipment.drop_address.state,
                        "drop_address_pincode": shipment.drop_address.pincode,
                        "drop_address_country": shipment.drop_address.country,
                        "drop_address_pk": shipment.drop_address.pk
                    }
                full_img_uri = None
                if shipment.img:
                    shipment_name = str(shipment.img.name)
                    full_img_uri = request.build_absolute_uri('/static/' + shipment_name.split('/')[-1])
                shipments.append({
                    "cost_of_courier": shipment.cost_of_courier,
                    "category": shipment.category,
                    "drop_address": drop_address,
                    "drop_name": shipment.drop_name,
                    "drop_phone": shipment.drop_phone,
                    "img": full_img_uri,
                    "item_name": shipment.item_name,
                    "weight": shipment.weight,
                    "price": shipment.price,
                    "barcode": shipment.barcode,
                    "real_tracking_no": shipment.real_tracking_no
                })
            promocode_type = None
            promocode_amount = None
            if order.promocode:
                if order.promocode.promocode_type:
                    promocode_type = order.promocode.promocode_type
                if order.promocode.promocode_amount:
                    promocode_amount = order.promocode.promocode_amount
            order_repr = {
                "address": order.address,
                "flat_no": order.flat_no,
                "name": Namemail.objects.get(pk=order.namemail.pk).name,
                "pincode": order.pincode,
                "pickup_time": order.time,
                "user": order.user,
                "promocode_type": promocode_type,
                "promocode_amount": promocode_amount
            }
            detailed_order = {
                "type": "b2c",
                "order": order_repr,
                "shipments": shipments
            }
            if len(detailed_order['shipments']) > 0:
                result.append(detailed_order)

        result.sort(key=lambda item: (item['order']['pickup_time']))

        bundle = {
            "pending_orders": result
        }
        self.log_throttled_access(request)
        return self.create_response(request, bundle)


class BarcodeResource(Resource):
    class Meta:
        resource_name = 'barcode_scan'
        authentication = Authentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('barcode_scan'), name="api_barcode_scan"),
        ]

    def barcode_scan(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        bid = request.GET.get('bid', '')
        if not bid:
            raise CustomBadRequest(
                code="request_invalid",
                message="No orders found. Please supply bid as a GET parameter")

        product = Product.objects.get(barcode=bid)
        order = BusinessOrder.objects.get(pk=product.order.pk)
        business = Business.objects.get(business_name=order.business)
        shipment = {
            "name": product.name,
            "quantity": product.quantity,
            "sku": product.sku,
            "price": product.price,
            "weight": product.weight,
            "real_tracking_no": product.real_tracking_no,
            "company": product.company,
            "shipping_cost": product.shipping_cost,
            "barcode": product.barcode
        }
        order_transformed = {
            "b_business_name": business.business_name,
            "b_username": business.username,
            "b_address": business.address,
            "b_contact_mob": business.contact_mob,
            "b_contact_office": business.contact_office,
            "b_name": business.name,
            "pickup_time": business.assigned_pickup_time,
            "b_pincode": business.pincode,
            "b_city": business.city,
            "b_state": business.state,
            "address1": order.address1,
            "address2": order.address2,
            "name": order.name,
            "phone": order.phone,
            "pincode": order.pincode,
            "order_id": order.pk,
        }
        result = [{"order": order_transformed, "shipments": [shipment]}]
        bundle = {
            "pending_orders": result
        }
        self.log_throttled_access(request)
        return self.create_response(request, bundle)