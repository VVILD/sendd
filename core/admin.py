from django.contrib import admin
from core.models import Warehouse, Pincode, Offline
import reversion
__author__ = 'vatsalshah'


class WarehouseAdmin(reversion.VersionAdmin):
    pass


admin.site.register(Warehouse, WarehouseAdmin)


class PincodeAdmin(reversion.VersionAdmin):
    list_display = ('pincode', 'division_name', 'region_name', 'circle_name', 'taluk', 'district_name', 'state_name', 'fedex_oda_opa', 'fedex_cod_service', 'fedex_servicable')
    search_fields = ('pincode', 'division_name', 'region_name', 'circle_name', 'taluk', 'district_name', 'state_name')
    list_filter = ('region_name', 'district_name', 'state_name', 'fedex_cod_service', 'fedex_oda_opa', 'fedex_servicable')

    def get_readonly_fields(self, request, obj=None):

        return [f.name for f in self.model._meta.fields]


admin.site.register(Pincode, PincodeAdmin)


class OfflineAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Offline, OfflineAdmin)