from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from core.models import Pincode
from businessapp.apiv3 import CORSModelResource

__author__ = 'vatsalshah'


class PincodeResource(CORSModelResource):
    class Meta:
        resource_name = 'pincode'
        authentication = Authentication()
        authorization = Authorization()
        object_class = Pincode
        queryset = Pincode.objects.all()
        allowed_methods = ['get']
        filtering = {
            "pincode": ALL
        }
