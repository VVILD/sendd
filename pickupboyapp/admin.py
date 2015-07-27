import datetime
from django.contrib import admin

from .models import *
from myapp.models import Order
from businessapp.models import Business
from .api import time_map


def print_html(arr):
    head = """
    <div class="bar"></div>
    <div class="timeline">
    """
    body = ""
    for item in arr:
        body += """
        <div class="entry">
        <h1>%s</h1>
        %s
        </div>
        """ % (item[0], item[1])
    end = "</div>"
    return head + body + end


class PickupboyAdmin(admin.ModelAdmin):
    search_fields = ['pincodes__pincode']
    list_display = ('name', 'pincodes_pref', 'alloted_times')

    def pincodes_pref(self, obj):
        return "\n".join([p.pincode for p in obj.pincodes.all()])

    @property
    def media(self):
        media = super(PickupboyAdmin, self).media
        css = {
            "all": (
                "css/custom.css",
            )
        }
        media.add_css(css)
        return media

    def alloted_times(self, obj):
        cust_orders = Order.objects.filter(pb=obj, order_status='A',
                                           date=datetime.date.today()).order_by("time").values("time")
        business = Business.objects.filter(pb=obj).values("pickup_time")
        cust_t = [(order['time'], 'Customer') for order in cust_orders]
        business_t = [(time_map[bo['pickup_time']][0], 'Business') for bo in business]
        all_t = cust_t + business_t
        all_t.sort(key=lambda x: (x[0]))
        new_list = []
        for t in all_t:
            new_list.append((t[0].strftime("%H:%M"), t[1]))
        html = print_html(new_list)
        return html

    alloted_times.allow_tags = True


admin.site.register(PBUser, PickupboyAdmin)


class PBPincodeAdmin(admin.ModelAdmin):
    pass


admin.site.register(PBPincodes, PBPincodeAdmin)