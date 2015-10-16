from django.http import HttpResponse
from tastypie import http
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import ModelResource, Resource, csrf_exempt
from businessapp.apiv3 import OnlyAuthorization
from businessapp.models import Business, AddressDetails, Product, Order

__author__ = 'vatsalshah'


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

    def delete_list(self, request, **kwargs):
        response = super(BaseCorsResource, self).delete_list(request, **kwargs)
        return self.add_cors_headers(response, True)

    def delete_detail(self, request, **kwargs):
        response = super(BaseCorsResource, self).delete_detail(request, **kwargs)
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
            response['Access-Control-Allow-Methods'] = "POST, PATCH, PUT, GET, DELETE"
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


class CORSModelResource(BaseCorsResource, ModelResource):
    pass


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
        authorization = Authorization()
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
