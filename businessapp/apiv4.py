from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from tastypie import http
from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import ImmediateHttpResponse, Unauthorized
from tastypie.http import HttpBadRequest
from tastypie.resources import ModelResource, Resource, csrf_exempt
from tastypie.utils import trailing_slash
from businessapp.models import Business, AddressDetails, Product, Order
from core.models import Pincode
from core.views import fedex_view_util
from pickupboyapp.exceptions import CustomBadRequest

__author__ = 'vatsalshah'

class OnlyAuthorization(Authorization):
    def read_list(self, object_list, bundle):
        business_username = bundle.request.GET.get("username", None)
        if business_username is None:
            raise ImmediateHttpResponse(HttpBadRequest("Please Provide a valid username key"))
        try:
            business_obj = Business.objects.get(username=business_username)
        except Business.DoesNotExist:
            raise ImmediateHttpResponse(HttpBadRequest("Username doesnt exist"))
        try:
            if bundle.request.META["HTTP_AUTHORIZATION"] == 'B' or business_obj.apikey == bundle.request.META[
                "HTTP_AUTHORIZATION"]:
                return object_list.filter(business=business_obj)
            else:
                raise Unauthorized
        except KeyError:
            raise ImmediateHttpResponse(HttpBadRequest("Provide valid authorization headers"))

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?

        # these 2 lines due to product wanting to use this authorisation
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'B'):
                return True

            return bundle.obj.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        try:
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'B'):
                return True

            return bundle.obj.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
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
            if (bundle.request.META["HTTP_AUTHORIZATION"] == 'B'):
                return True

            return bundle.obj.business.apikey == bundle.request.META["HTTP_AUTHORIZATION"]
        except:
            return False

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")



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
        response = super(BaseCorsResource, self).post_detail(request, **kwargs)
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
            'pickup_address': ALL_WITH_RELATIONS,
            'status': ALL
        }


class ProductResource(CORSModelResource):
    order = fields.ToOneField(OrderResource, 'order', full=True)

    class Meta:
        queryset = Product.objects.all()
        resource_name = 'product'
        authorization = Authorization()
        authentication = Authentication()


class FedexCheckResource(BaseCorsResource):
    class Meta:
        resource_name = 'fedex_check'
        authentication = Authentication()
        authorization = OnlyAuthorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('fedex_check'), name="api_fedex_check"),
        ]

    def fedex_check(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        pincode = request.GET.get('pincode', None)

        if pincode is None:
            raise CustomBadRequest(code="error", message="Please supply a valid pincode")

        db_pincode = list(Pincode.objects.filter(pincode=pincode).values())

        self.log_throttled_access(request)
        return self.create_response(request, db_pincode[0] if len(db_pincode) > 0 else None)


class ReverseOrderResource(BaseCorsResource):
    class Meta:
        resource_name = 'reverse_order'
        authentication = Authentication()
        authorization = OnlyAuthorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('reverse_order'), name="api_reverse_order"),
        ]

    def reverse_order(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        self.throttle_check(request)
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        order_no = data.get('order_no', None)
        tracking_ids = data.get('tracking_ids', None)
        username = data.get('username', None)

        if not (username and order_no and tracking_ids):
            raise CustomBadRequest(code="error",
                                   message="Please supply valid parameters. order_no, tracking_ids and username")

        try:
            existing_order = Order.objects.get(business__username=username, pk=order_no)
        except ObjectDoesNotExist:
            raise CustomBadRequest(code="error", message="No corresponding order found")

        products = existing_order.product_set.filter(real_tracking_no__in=tracking_ids)
        if products.count() == 0:
            raise CustomBadRequest(code="error", message="No tracking ids found")

        temp_pickup_address = AddressDetails(
            company_name=str(existing_order.name),
            contact_person=str(existing_order.name),
            phone_office=str(existing_order.phone),
            address=str(existing_order.address1) + " " + str(existing_order.address2),
            city=str(existing_order.city),
            state=str(existing_order.state),
            pincode=str(existing_order.pincode)
        )
        temp_pickup_address.save()

        try:
            new_order = Order(
                reference_id=str(existing_order.order_no),
                name=existing_order.pickup_address.company_name.decode('utf-8'),
                phone=existing_order.pickup_address.phone_office.decode('utf-8'),
                email=existing_order.pickup_address.email.decode('utf-8') if existing_order.pickup_address.email is not None else None,
                address1=existing_order.pickup_address.address.decode('utf-8'),
                city=existing_order.pickup_address.city.decode('utf-8'),
                state=str(existing_order.pickup_address.state),
                pincode=existing_order.pickup_address.pincode.decode('utf-8'),
                country='India',
                payment_method='F',
                method=str(existing_order.method),
                business=existing_order.business,
                pickup_address=temp_pickup_address,
                is_reverse=True
            )
            new_order.save()
        except Exception, e:
            temp_pickup_address.delete()
            raise CustomBadRequest(code="error", message=str(e))

        new_products = []
        try:
            for product in products:
                new_product = Product(
                    name=str(product.name),
                    quantity=int(product.quantity),
                    sku=str(product.sku),
                    price=float(product.price),
                    weight=float(product.weight) if product.weight else None,
                    applied_weight=float(product.applied_weight),
                    order=new_order,
                    company='F',
                    shipping_cost=float(product.shipping_cost),
                    is_document=product.is_document,
                    is_fragile=product.is_fragile
                )
                new_product.save()
                new_products.append(new_product)
        except Exception, e:
            temp_pickup_address.delete()
            new_order.delete()
            for np in new_products:
                np.delete()
            raise CustomBadRequest(code="error", message=str(e))

        try:
            response = fedex_view_util(new_order.pk, 'business')
        except Exception, e:
            temp_pickup_address.delete()
            new_order.delete()
            for np in new_products:
                np.delete()
            raise CustomBadRequest(code="error", message=str(e))

        existing_order.reversed = True
        existing_order.save()

        self.log_throttled_access(request)
        return self.create_response(request, response)
