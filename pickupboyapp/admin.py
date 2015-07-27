import datetime
from django.contrib import admin

from .models import *
from myapp.models import Order
from businessapp.models import Business
from .api import time_map


class PickupboyAdmin(admin.ModelAdmin):
    search_fields = ['pincodes__pincode']
    list_display = ('name', 'pincodes_pref', 'alloted_times')

    def pincodes_pref(self, obj):
        return "\n".join([p.pincode for p in obj.pincodes.all()])

    def alloted_times(self, obj):
        cust_orders = Order.objects.filter(pb=obj, order_status='A',
                                           date=datetime.date.today()).order_by("time").values("time")
        business = Business.objects.filter(pb=obj).values("pickup_time")
        cust_t = [(order['time'], 'c') for order in cust_orders]
        business_t = [(time_map[bo['pickup_time']][0], 'b') for bo in business]
        all_t = cust_t + business_t
        all_t.sort(key=lambda x: (x[0]))
        new_list = []
        for t in all_t:
            new_list.append((t[0].strftime("%H:%M"), t[1]))
        return ', '.join(map(str, new_list))


admin.site.register(PBUser, PickupboyAdmin)


class PBPincodeAdmin(admin.ModelAdmin):
    pass


admin.site.register(PBPincodes, PBPincodeAdmin)