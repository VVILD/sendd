from django.contrib import admin

from .models import *


class PickupboyAdmin(admin.ModelAdmin):
    search_fields = ['pincodes__pincode']
    list_display = ('name', 'get_pincodes')

    def get_pincodes(self, obj):
        return "\n".join([p.pincode for p in obj.pincodes.all()])


admin.site.register(PBUser, PickupboyAdmin)


class PBPincodeAdmin(admin.ModelAdmin):
    pass


admin.site.register(PBPincodes, PBPincodeAdmin)