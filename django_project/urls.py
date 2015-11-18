from django.conf.urls import patterns, include, url
from django.contrib import admin
from businessapp.views import print_address_view,readpdf,barcode_stats_view,qc_stats_view,print_invoice_order_view,print_invoice_product_view
from core.views import create_fedex_shipment, barcode_fedex_redirector, create_individual_fedex_shipment, \
    create_ecom_shipment, download_ecom_orders, schedule_reverse_pickup
from myapp.api import UserResource,AddressResource,OrderResource,ShipmentResource,XResource,LoginSessionResource,WeborderResource,PriceappResource,DateappResource,ForgotpassResource
from tastypie.api import Api
from django_project import settings
from myapp.api import *
from pickupboyapp.api import PickupboyResource, PBLocationsResource, PBUserResource, BarcodeResource
from pickupboyapp.views import pb_location_view


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

from myapp.apiv2 import UserResource2, AddressResource2, OrderResource2, ShipmentResource2, XResource2, \
    LoginSessionResource2, WeborderResource2, PriceappResource2, DateappResource2, ForgotpassResource2, \
    NamemailResource2, PromocheckResource2, PromocodeResource2, PincodecheckResource2, InvoicesentResource2, \
    ZipcodeResource2



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

from myapp.apiv3 import ShipmentResource3,OrderResource3, UserResource3, NamemailResource3, AddressResource3

v3_api = Api(api_name='v3')
v3_api.register(OrderResource3())
v3_api.register(ShipmentResource3())
v3_api.register(UserResource3())
v3_api.register(NamemailResource3())
v3_api.register(AddressResource3())


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
pbv1_api.register(PBLocationsResource())
pbv1_api.register(PBUserResource())
pbv1_api.register(BarcodeResource())

from businessapp.apiv2 import ProductResource2, InvoiceResource, TrackingResource, SearchResource, BarcodeAllotmentResource, BarcodeFetchResource
from businessapp.apiv2 import OrderResource as OrderResource2
bv2_api = Api(api_name='v2')
bv2_api.register(ProductResource2())
bv2_api.register(InvoiceResource())
bv2_api.register(TrackingResource())
bv2_api.register(SearchResource())
bv2_api.register(OrderResource2())
bv2_api.register(BarcodeAllotmentResource())
bv2_api.register(BarcodeFetchResource())

from businessapp.apiv3 import ProductResource3, OrderResource3, ShippingEstimateResource, OrderPatchResource, BusinessPatchResource,OrderCancelResource,PincodecheckResource, OrderPatchReferenceResource, EmailLabelsResource
from businessapp.apiv3 import TrackingResource as TrackingResourceV3
bv3_api = Api(api_name='v3')
bv3_api.register(ProductResource3())
bv3_api.register(OrderResource3())
bv3_api.register(ShippingEstimateResource())
bv3_api.register(OrderPatchResource())
bv3_api.register(TrackingResourceV3())
bv3_api.register(BusinessPatchResource())
bv3_api.register(OrderCancelResource())
bv3_api.register(PincodecheckResource())
bv3_api.register(OrderPatchReferenceResource())
bv3_api.register(EmailLabelsResource())


from businessapp.apiv4 import BusinessResource as BusinessResourceV4, ReverseOrderResource
from businessapp.apiv4 import OrderResource as OrderResourceV4
from businessapp.apiv4 import ProductResource as ProductResourceV4
from businessapp.apiv4 import FedexCheckResource as FedexCheckResourceV4
from businessapp.apiv4 import BusinessPickupAddressResource
bv4_api = Api(api_name='v4')
bv4_api.register(BusinessResourceV4())
bv4_api.register(BusinessPickupAddressResource())
bv4_api.register(ProductResourceV4())
bv4_api.register(OrderResourceV4())
bv4_api.register(FedexCheckResourceV4())
bv4_api.register(ReverseOrderResource())

from core.api import PincodeResource
pv1_api = Api(api_name='v1')
pv1_api.register(PincodeResource())


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shippanda.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/', include(v2_api.urls)),
    url(r'^api/', include(v3_api.urls)),
    url(r'^bapi/', include(bv1_api.urls)),
    url(r'^bapi/', include(bv2_api.urls)),
    url(r'^bapi/', include(bv3_api.urls)),
    url(r'^bapi/', include(bv4_api.urls)),
    url(r'^papi/', include(pv1_api.urls)),
    url(r'^stats/', include('myapp.urls')),       
    url(r'^pb_api/', include(pbv1_api.urls)),
    url(r'^pb_location/', pb_location_view, name='pb_location'),
    url(r'^create_fedex_shipment/', create_fedex_shipment, name='create_fedex'),
    url(r'^create_ecom_shipment/', create_ecom_shipment, name='create_ecom_shipment'),
    url(r'^create_fedex_legacy/', create_individual_fedex_shipment, name='create_fedex_legacy'),
    url(r'^print_address/', print_address_view, name='print_business_address'),
    url(r'^print_invoice/', print_invoice_order_view, name='print_invoice_order_view'),
    url(r'^print_invoice2/', print_invoice_product_view, name='print_invoice_product_view'),
    url(r'^barcode_stats/', barcode_stats_view, name='barcode_stats'),
    url(r'^qc_stats/', qc_stats_view, name='qc_stats'),
    url(r'^ffmanual/', readpdf, name='readpdf'),
    url(r'^barcode_fedex_print/(?P<barcode>[\w]{10})/$', barcode_fedex_redirector, name='fedex_barcode_redirector'),
    url(r'^download_ecom_orders/', download_ecom_orders, name='download_ecom_orders'),
    url(r'^fedex_pickup_scheduler/$', schedule_reverse_pickup, name='fedex_pickup_scheduler')
)

urlpatterns += patterns('',
    (r'^django-rq/', include('django_rq.urls')),
)