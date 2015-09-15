from django.conf.urls import url
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.utils import trailing_slash
from core.models import Pincode
from businessapp.apiv3 import CORSModelResource, CORSResource
from myapp.models import Zipcode
from pickupboyapp.exceptions import CustomBadRequest

__author__ = 'vatsalshah'


class PincodeResource(CORSResource):
    class Meta:
        resource_name = 'pincode'
        authentication = Authentication()
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('pincode_check'), name="api_pincode_check"),
        ]

    def pincode_check(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        pincode = request.GET.get('pincode', None)
        if not pincode:
            raise CustomBadRequest(
                code="request_invalid",
                message="No pincode. Please supply pincode as a GET parameter")

        bundle = {}
        pincodes = Pincode.objects.filter(pincode=pincode)
        if len(pincodes) < 1:
            zipcodes = Zipcode.objects.filter(pincode=pincode)
            if len(zipcodes) > 0:
                for zipcode in zipcodes:
                    bundle = {
                        "city": zipcode.city,
                        "state": zipcode.state,
                        "pincode": zipcode.pincode,
                        "cod_service": zipcode.cod
                    }
                    break
        else:
            for pincode in pincodes:
                if not pincode.fedex_cod_service:
                    zipcodes = Zipcode.objects.filter(pk=pincode.pincode)
                    if len(zipcodes) > 0:
                        for zipcode in zipcodes:
                            if not zipcode.cod:
                                bundle = {
                                    "city": pincode.district_name,
                                    "state": pincode.state_name,
                                    "pincode": pincode.pincode,
                                    "cod_service": pincode.fedex_cod_service
                                }
                                break
                            else:
                                bundle = {
                                    "city": zipcode.city,
                                    "state": zipcode.state,
                                    "pincode": zipcode.pincode,
                                    "cod_service": zipcode.cod
                                }
                                break
                    else:
                        bundle = {
                            "city": pincode.district_name,
                            "state": pincode.state_name,
                            "pincode": pincode.pincode,
                            "cod_service": pincode.fedex_cod_service
                        }
                        break
                else:
                    bundle = {
                        "city": pincode.district_name,
                        "state": pincode.state_name,
                        "pincode": pincode.pincode,
                        "cod_service": pincode.fedex_cod_service
                    }
                    break

        self.log_throttled_access(request)
        return self.create_response(request, bundle)
