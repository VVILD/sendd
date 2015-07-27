import datetime
from django.contrib import admin

from .models import *
from myapp.models import Order
from businessapp.models import Business


class PickupboyAdmin(admin.ModelAdmin):
    search_fields = ['pincodes__pincode']
    list_display = ('name', 'pincodes_pref', 'alloted_times')

    def pincodes_pref(self, obj):
        return "\n".join([p.pincode for p in obj.pincodes.all()])

    def alloted_times(self, obj):
        cust_orders = Order.objects.filter(pb=obj, order_status='A',
                                           date=datetime.date.today()).order_by("time").values("time")
        business = Business.objects.filter(pb=obj).values("pickup_time")
        cust_t = [(order['time'].strftime("%H:%M"), 'c') for order in cust_orders]
        business_t = [(str(bo['pickup_time']), 'b') for bo in business]
        all_t = cust_t + business_t
        return ', '.join(map(str, all_t))


admin.site.register(PBUser, PickupboyAdmin)


class PBPincodeAdmin(admin.ModelAdmin):
    pass


admin.site.register(PBPincodes, PBPincodeAdmin)