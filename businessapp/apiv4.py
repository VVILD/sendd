from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from businessapp.apiv3 import CORSModelResource, OnlyAuthorization
from businessapp.models import Business, AddressDetails, Product, Order

__author__ = 'vatsalshah'


class OnlyAuthorizationPickup(Authorization):
    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?

        # these 2 lines due to product wanting to use this authorisation
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'A'):
                return True

            return bundle.obj.order.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'A'):
                return True

            return bundle.obj.order.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
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
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'A'):
                return True

            return bundle.obj.order.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

    def delete_list(self, object_list, bundle):
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'A'):
                return True

            return bundle.obj.order.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

    def delete_detail(self, object_list, bundle):
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'A'):
                return True

            return bundle.obj.order.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False


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
        authorization = OnlyAuthorizationPickup()
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
        authorization = Authorization()
        authentication = Authentication()