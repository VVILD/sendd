from django.contrib import admin
from core.models import Warehouse, Pincode, Offline

__author__ = 'vatsalshah'


class WarehouseAdmin(admin.ModelAdmin):
    pass


admin.site.register(Warehouse, WarehouseAdmin)


class PincodeAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'division_name', 'region_name', 'circle_name', 'taluk', 'district_name', 'state_name', 'fedex_oda_opa', 'fedex_cod_service', 'fedex_servicable')
    search_fields = ('pincode', 'division_name', 'region_name', 'circle_name', 'taluk', 'district_name', 'state_name')
    list_filter = ('region_name', 'district_name', 'state_name', 'fedex_cod_service', 'fedex_oda_opa', 'fedex_servicable')

    def get_readonly_fields(self, request, obj=None):

        return [f.name for f in self.model._meta.fields]


admin.site.register(Pincode, PincodeAdmin)


class OfflineAdmin(admin.ModelAdmin):
    pass

admin.site.register(Offline, OfflineAdmin)