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

        if format.startswith('multipart'):
            data = request.POST.copy()
            data.update(request.FILES)

            return data

        return super(MultipartResource, self).deserialize(request, data, format)



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
    img = fields.FileField(attribute="img", null=True, blank=True)

    class Meta:
        queryset = Shipment.objects.all()
        resource_name = 'shipment'
        authorization = Authorization()
        authentication = Authentication()
        always_return_data = True



class NamemailResource3(ModelResource):
    user = fields.ForeignKey(UserResource3, 'user',full=True)

    class Meta:
        queryset = Namemail.objects.all()
        resource_name = 'namemail'
        authorization = Authorization()
        always_return_data = True

