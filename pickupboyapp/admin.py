import datetime
import json
from django.contrib import admin

from .models import *
from myapp.models import Order
from businessapp.models import Business
from .api import time_map
import reversion

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


class PickupboyAdmin(reversion.VersionAdmin):
    search_fields = ['pincodes__pincode','name']
    list_display = ('name', 'pincodes_pref', 'alloted_times')
    change_list_template='pickupboyapp/templates/admin/pickupboyapp/change_list.html'


    def queryset(self, request):
        qs = super(PickupboyAdmin, self).queryset(request)
        qs = qs.filter(status='A')
        return qs

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
        business = Business.objects.filter(pb=obj, assigned_pickup_time__isnull=False).values("assigned_pickup_time")
        cust_t = [(order['time'], 'Customer') for order in cust_orders]
        business_t = [(bo['assigned_pickup_time'], 'Business') for bo in business]
        all_t = cust_t + business_t
        all_t.sort(key=lambda x: (x[0]))
        new_list = []
        for t in all_t:
            new_list.append((t[0].strftime("%H:%M"), t[1]))
        html = print_html(new_list)
        return html

    def changelist_view(self, request, extra_context=None):
        location_map = []
        pb_users = PBUser.objects.all()
        for pb_user in pb_users:
            pb_location = PBLocations.objects.filter(pbuser=pb_user).order_by('-updated_at')
            if len(pb_location) > 0:
                location_map.append([pb_user.name, pb_location[0].lat, pb_location[0].lon])
        location_map_json = json.dumps(location_map)
        return super(PickupboyAdmin, self).changelist_view(request, extra_context={"location_map": location_map_json})

    alloted_times.allow_tags = True


admin.site.register(PBUser, PickupboyAdmin)


class CheckappAdmin(reversion.VersionAdmin):
    search_fields = ['phone','name']
    list_display = ('name', 'phone', 'count')
    search_fields= ['name','phone']

    def count(self, obj):
        return PBLocations.objects.filter(pbuser=obj).count()

admin.site.register(Checkapp, CheckappAdmin)

class PBPincodeAdmin(reversion.VersionAdmin):
    pass

admin.site.register(PBPincodes, PBPincodeAdmin)




class PBLocationsAdmin(reversion.VersionAdmin):
    list_display = ['pbuser','updated_at','lat','lon']
    list_filter = ['pbuser__name','pbuser__phone']
    search_fields = ['pbuser__name','pbuser__phone']

admin.site.register(PBLocations, PBLocationsAdmin)