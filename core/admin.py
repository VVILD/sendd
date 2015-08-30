from django.contrib import admin
from core.models import Warehouse

__author__ = 'vatsalshah'


class WarehouseAdmin(admin.ModelAdmin):
    pass


admin.site.register(Warehouse, WarehouseAdmin)