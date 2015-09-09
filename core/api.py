from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from core.models import Pincode

__author__ = 'vatsalshah'


class PincodeResource(ModelResource):
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
