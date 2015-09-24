from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from myapp.models import Order, Shipment, Namemail, User, Address


class UserResource3(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization = Authorization()
        always_return_data = True

class OrderResource3(ModelResource):
    namemail = fields.ForeignKey('myapp.apiv3.NamemailResource3', 'namemail', null=True)
    shipments = fields.ToManyField("myapp.apiv3.ShipmentResource3", 'shipment_set', related_name='shipment')
    user = fields.ForeignKey(UserResource3, 'user')

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

class ShipmentResource3(ModelResource):
    order = fields.ToOneField(OrderResource3, 'order')
    drop_address = fields.ForeignKey(AddressResource3, 'drop_address')

    class Meta:
        queryset = Shipment.objects.all()
        resource_name = 'shipment'
        authorization = Authorization()
        authentication = Authentication()
        always_return_data = True



class NamemailResource3(ModelResource):
    user = fields.ForeignKey(UserResource3, 'user')

    class Meta:
        queryset = Namemail.objects.all()
        resource_name = 'namemail'
        authorization = Authorization()
        always_return_data = True

