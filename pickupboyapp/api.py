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
from myapp.models import Order, Shipment
from .models import PBLocations, PBUser


__author__ = 'vatsalshah'


class PBUserResource(ModelResource):
    class Meta:
        resource_name = 'pb_users'
        object_class = PBUser
        queryset = PBUser.objects.all()
        allowed_methods = ['get']
        authorization = Authorization()

    def dehydrate(self, bundle):
        bundle.data['otp'] = randint(1000, 9999)
        msg0 = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
        msga = str(bundle.data['phone'])
        msg1 = "&msg=Welcome+to+Sendd.+Your+OTP+is+"
        msg2 = str(bundle.data['otp'])
        msg3 = ".This+message+is+for+automated+verification+purpose.+No+action+required.&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&v=1.1&format=text"
        # url1="http://49.50.69.90//api/smsapi.aspx?username=doormint&password=naman123&to="+ str(bundle.data['phone']) +"&from=DORMNT&message="
        query = ''.join([msg0, msga, msg1, msg2, msg3])
        print query
        x = urllib2.urlopen(query).read()
        print x
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
        print(pb_ph)
        if not pb_ph:
            raise CustomBadRequest(
                code="request_invalid",
                message="No user id found. Please supply uid as a GET parameter")
        result = []
        pending_orders = Order.objects.filter(pb__phone=pb_ph, order_status='A', date=datetime.date.today()).order_by(
            "time")
        for order in pending_orders:
            detailed_order = {}
            order_json = serializers.serialize('json', [order])
            detailed_order['order'] = order_json
            detailed_order['shipments'] = serializers.serialize('json', Shipment.objects.filter(order=order).all())
            result.append(detailed_order)

        bundle = {
            "pending_orders": result
        }
        self.log_throttled_access(request)
        return self.create_response(request, bundle)