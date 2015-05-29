from django.conf.urls import patterns, include, url
from django.contrib import admin
from myapp.api import UserResource,AddressResource,OrderResource,ShipmentResource,XResource,LoginSessionResource,WeborderResource,PriceappResource,DateappResource,ForgotpassResource
from tastypie.api import Api


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

from myapp.apiv2 import UserResource2,AddressResource2,OrderResource2,ShipmentResource2,XResource2,LoginSessionResource2,WeborderResource2,PriceappResource2,DateappResource2,ForgotpassResource2,NamemailResource2,PromocheckResource2,PromocodeResource2,PincodecheckResource2



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

from businessapp.api import BusinessResource,LoginSessionResource,OrderResource,ProductResource
bv1_api = Api(api_name='v1')
bv1_api.register(BusinessResource())
bv1_api.register(LoginSessionResource())
bv1_api.register(OrderResource())
bv1_api.register(ProductResource())
bv1_api.register(XResource())



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shippanda.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
 	url(r'^api/', include(v2_api.urls)),
 	url(r'^bapi/', include(bv1_api.urls)),       
)
