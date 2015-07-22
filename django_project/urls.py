from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api

from myapp.api import UserResource, AddressResource, ShipmentResource, WeborderResource, PriceappResource, \
    DateappResource
from pickupboyapp.api import PickupboyResource


v1_api = Api(api_name='v1')
v1_api.register(UserResource())
v1_api.register(AddressResource())
v1_api.register(OrderResource())
v1_api.register(ShipmentResource())
v1_api.register(XResource())
v1_api.register(LoginSessionResource())
v1_api.register(WeborderResource())
v1_api.register(PriceappResource())
v1_api.register(DateappResource())
v1_api.register(ForgotpassResource())

from myapp.apiv2 import UserResource2,AddressResource2,OrderResource2,ShipmentResource2,XResource2,LoginSessionResource2,WeborderResource2,PriceappResource2,DateappResource2,ForgotpassResource2,NamemailResource2,PromocheckResource2,PromocodeResource2,PincodecheckResource2,InvoicesentResource2,ZipcodeResource2



v2_api = Api(api_name='v2')
v2_api.register(UserResource2())
v2_api.register(AddressResource2())
v2_api.register(OrderResource2())
v2_api.register(ShipmentResource2())
v2_api.register(XResource2())
v2_api.register(LoginSessionResource2())
v2_api.register(WeborderResource2())
v2_api.register(PriceappResource2())
v2_api.register(DateappResource2())
v2_api.register(ForgotpassResource2())
v2_api.register(NamemailResource2())
v2_api.register(PromocheckResource2())
v2_api.register(PromocodeResource2())
v2_api.register(PincodecheckResource2())
v2_api.register(InvoicesentResource2())
v2_api.register(ZipcodeResource2())



from businessapp.api import BusinessResource,LoginSessionResource,OrderResource,ProductResource,XResource,UsernamecheckResource,PaymentResource,PricingResource,ForgotpassResource,ChangepassResource,BillingResource,PincodecheckResource
bv1_api = Api(api_name='v1')
bv1_api.register(BusinessResource())
bv1_api.register(LoginSessionResource())
bv1_api.register(OrderResource())
bv1_api.register(ProductResource())
bv1_api.register(XResource())
bv1_api.register(UsernamecheckResource())
bv1_api.register(PaymentResource())
bv1_api.register(PricingResource())
bv1_api.register(ChangepassResource())
bv1_api.register(ForgotpassResource())
bv1_api.register(BillingResource())
bv1_api.register(PincodecheckResource())

pbv1_api = Api(api_name='v1')
pbv1_api.register(PickupboyResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shippanda.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
 	url(r'^api/', include(v2_api.urls)),
 	url(r'^bapi/', include(bv1_api.urls)),
    url(r'^stats/', include('myapp.urls')),
    url(r'^pb_api/', include(pbv1_api.urls)),
)
