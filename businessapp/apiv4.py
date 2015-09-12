from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from businessapp.apiv3 import CORSModelResource, OnlyAuthorization
from businessapp.models import Business, AddressDetails, Product, Order

__author__ = 'vatsalshah'


class BusinessResource(CORSModelResource):
    class Meta:
        object_class = Business
        queryset = Business.objects.all()
        resource_name = 'business'
        authentication = Authentication()
        authorization = OnlyAuthorization()
        fields = ['username', 'business_name', 'email', 'name', 'contact_mob', 'contact_office']
        filtering = {
            'username': ALL,
            'business_name': ALL
        }


class BusinessPickupAddressResource(CORSModelResource):
    business = fields.ForeignKey(BusinessResource, 'business', full=True)

    class Meta:
        resource_name = 'pickup_address'
        object_class = AddressDetails
        queryset = AddressDetails.objects.all()
        authorization = OnlyAuthorization()
        authentication = Authentication()
        always_return_data = True
        filtering = {
            'business': ALL_WITH_RELATIONS
        }


class OrderResource(CORSModelResource):
    business = fields.ForeignKey(BusinessResource, 'business', full=True)
    products = fields.ToManyField("businessapp.apiv4.ProductResource", 'product_set', related_name='product')
    pickup_address = fields.ForeignKey(BusinessPickupAddressResource, 'pickup_address', full=True)

    class Meta:
        queryset = Order.objects.all()
        resource_name = 'order'
        authorization = OnlyAuthorization()
        authentication = Authentication()
        always_return_data = True
        ordering = ['book_time']
        filtering = {
            'business': ALL_WITH_RELATIONS,
            'pickup_address': ALL_WITH_RELATIONS
        }


class ProductResource(CORSModelResource):
    order = fields.ToOneField(OrderResource, 'order', full=True)

    class Meta:
        queryset = Product.objects.all()
        resource_name = 'product'
        authorization = OnlyAuthorization()
        authentication = Authentication()