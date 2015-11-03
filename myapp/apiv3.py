import base64
import random
import datetime
from django.core.files.base import ContentFile
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource

from core.models import Offline
from myapp.models import Order, Shipment, Namemail, User, Address, Promocode
from pickupboyapp.exceptions import CustomBadRequest
from dateutil.parser import parse


class MultipartResource(object):

    def deserialize(self, request, data, format=None):

        if not format:
            format = request.META.get('CONTENT_TYPE', 'application/json')

        if format == 'application/x-www-form-urlencoded':
            return request.POST

        if format.startswith('multipart/form-data'):
            multipart_data = request.POST.copy()
            multipart_data.update(request.FILES)
            return multipart_data

        return super(MultipartResource, self).deserialize(request, data, format)

    def put_detail(self, request, **kwargs):
        if request.META.get('CONTENT_TYPE', '').startswith('multipart/form-data') and not hasattr(request, '_body'):
            request._body = ''
        return super(MultipartResource, self).put_detail(request, **kwargs)

    def patch_detail(self, request, **kwargs):
        if request.META.get('CONTENT_TYPE', '').startswith('multipart/form-data') and not hasattr(request, '_body'):
            request._body = ''
        return super(MultipartResource, self).patch_detail(request, **kwargs)



class UserResource3(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization = Authorization()
        always_return_data = True

class OrderResource3(ModelResource):
    namemail = fields.ForeignKey('myapp.apiv3.NamemailResource3', 'namemail', null=True,full=True)
    shipments = fields.ToManyField("myapp.apiv3.ShipmentResource3", 'shipment_set', related_name='shipment',full=True)
    user = fields.ForeignKey(UserResource3, 'user',full=True)

    class Meta:
        queryset = Order.objects.all()
        resource_name = 'order'
        authorization = Authorization()
        authentication = Authentication()
        allowed_methods = ['get','post', 'patch', 'put']
        always_return_data = True

    def hydrate(self, bundle):

        offline = None
        try:
            check_time = datetime.datetime.combine(parse(str(bundle.data['date'])).date(), datetime.datetime.strptime(bundle.data['time'], "%I:%M %p").time())
            offline = Offline.objects.filter(start__lte=check_time, end__gte=check_time, active=True).values("message")
            if len(offline) > 0:
                raise CustomBadRequest(
                    code="offline",
                    message=offline[0]['message']
                )
        except:
            if offline is not None:
                if len(offline) > 0:
                    raise CustomBadRequest(
                        code="offline",
                        message=offline[0]['message']
                    )
            pass

        try:
            promocode = Promocode.objects.get(pk=bundle.data['code'])

            if (promocode.only_for_first == 'Y'):

                shipment = Shipment.objects.filter(order__user=bundle.data['user'], order__way='A')  # pk is the number

                if (shipment.count() == 0):
                    # everything good
                    bundle.data['promocode'] = "/api/v2/promocode/" + str(promocode.pk) + "/"
                    bundle.data['valid'] = 'Y'
                else:
                    bundle.data['promomsg'] = "You are not a first time user"
            else:
                bundle.data['promocode'] = "/api/v2/promocode/" + str(promocode.pk) + "/"
        except:
            bundle.data['promomsg'] = "Wrong promo code"



class AddressResource3( ModelResource):
    class Meta:
        queryset = Address.objects.all()
        resource_name = 'address'
        authorization = Authorization()
        always_return_data = True

class ShipmentResource3(MultipartResource,ModelResource):
    order = fields.ToOneField(OrderResource3, 'order')
    drop_address = fields.ForeignKey(AddressResource3, 'drop_address',full=True)
    image = fields.CharField(null=True, blank=True)
    img = fields.FileField(attribute='img', null=True, blank=True)

    class Meta:
        queryset = Shipment.objects.all()
        resource_name = 'shipment'
        authorization = Authorization()
        authentication = Authentication()
        always_return_data = True

    def hydrate(self, bundle):
        if 'image' in bundle.data:
            if bundle.data['image']:
                bundle.data['img'] = ContentFile(base64.b64decode(str(bundle.data['image'])), str(bundle.data['image'])[:10] + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + ".jpeg")

        return bundle


class NamemailResource3(ModelResource):
    user = fields.ForeignKey(UserResource3, 'user',full=True)

    class Meta:
        queryset = Namemail.objects.all()
        resource_name = 'namemail'
        authorization = Authorization()
        always_return_data = True

