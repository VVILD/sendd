import base64
from django.core.files.base import ContentFile
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from myapp.models import Order, Shipment, Namemail, User, Address


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

    class Meta:
        queryset = Shipment.objects.all()
        resource_name = 'shipment'
        authorization = Authorization()
        authentication = Authentication()
        always_return_data = True

    def hydrate(self, bundle):
        if bundle.data['image']:
            bundle.data['img'] = ContentFile(base64.b64decode(bundle.data['image']))

        return bundle


class NamemailResource3(ModelResource):
    user = fields.ForeignKey(UserResource3, 'user',full=True)

    class Meta:
        queryset = Namemail.objects.all()
        resource_name = 'namemail'
        authorization = Authorization()
        always_return_data = True

