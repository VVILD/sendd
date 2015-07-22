import datetime

from django.conf.urls import url
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from tastypie.resources import Resource
from tastypie.utils import trailing_slash

from pickupboyapp.exceptions import CustomBadRequest
from myapp.models import Order


__author__ = 'vatsalshah'


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
                message="No user id found. Please supply uid as a GET parameter")

        pending_orders = Order.objects.filter(pickupboy__phone=pb_ph, order_status='A',
                                              date=datetime.date.today()).order_by("time")

        bundle = {
            "pending_orders": pending_orders
        }
        self.log_throttled_access(request)
        return self.create_response(request, bundle)