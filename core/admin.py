from django.contrib import admin
from core.models import Warehouse, Pincode

__author__ = 'vatsalshah'


class WarehouseAdmin(admin.ModelAdmin):
    pass


admin.site.register(Warehouse, WarehouseAdmin)


class PincodeAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'division_name', 'region_name', 'circle_name', 'taluk', 'district_name', 'state_name', 'fedex_oda_opa', 'fedex_cod_service', 'fedex_servicable')
    search_fields = ('pincode', 'division_name', 'region_name', 'circle_name', 'taluk', 'district_name', 'state_name')
    list_filter = ('region_name', 'district_name', 'state_name', 'fedex_cod_service', 'fedex_oda_opa', 'fedex_servicable')

admin.site.register(Pincode, PincodeAdmin)