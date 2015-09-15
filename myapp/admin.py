from django.contrib import admin
from .models import *
from myapp.forms import ShipmentForm, OrderForm, OrderEditForm
from businessapp.models import Profile

import json
# Register your models here.
from django.http import HttpResponse, HttpResponseRedirect
import urllib
from django.shortcuts import redirect
from datetime import date
import datetime
from django.db.models import Avg, Sum, Q
from datetime import timedelta


class UserAdmin(admin.ModelAdmin):
    search_fields = ['phone', 'name']
    list_display = ('phone', 'name', 'otp', 'apikey', 'email', 'time')
    list_editable = ('name',)


admin.site.register(User, UserAdmin)


class AddressAdmin(admin.ModelAdmin):
    def response_change(self, request, obj):
        print self
        print "sdddddddddddddddddddddddddddd"
        # return super(UserAdmin, self).response_change(request, obj)
        return HttpResponse('''
   <script type="text/javascript">
	  opener.dismissAddAnotherPopup(window);
   </script>''')


admin.site.register(Address, AddressAdmin)


class NamemailAdmin(admin.ModelAdmin):
    def response_change(self, request, obj):
        print self
        print "sdddddddddddddddddddddddddddd"
        # return super(UserAdmin, self).response_change(request, obj)
        return HttpResponse('''
   <script type="text/javascript">
	  opener.dismissAddAnotherPopup(window);
   </script>''')


admin.site.register(Namemail, NamemailAdmin)
'''

class ShipmentInline(admin.TabularInline):
	model = Shipment
	form=ShipmentForm
	suit_classes = 'suit-tab suit-tab-shipments'
	#readonly_fields = ('real_tracking_no','print_invoice',)
	fieldsets=(
	('Basic Information', {'fields':['real_tracking_no','print_invoice',], 'classes':('suit-tab','suit-tab-general')}),
		#('Address', {'fields':['flat_no','address','pincode',], 'classes':('suit-tab','suit-tab-general')}),
		#('Destination Address', {'fields':['drop_name','drop_phone','drop_flat_no','locality','city','state','drop_pincode','country'] , 'classes':['collapse',]})
		#('Invoices',{'fields':['send_invoice',], 'classes':('suit-tab','suit-tab-invoices')})
	)
	suit_form_tabs = (('general', 'General'))
'''


class PickupboyAdmin(admin.ModelAdmin):
    search_fields = ['name', 'phone']
    list_display = ['name', 'phone']
    pass


# admin.site.register(Pickupboy,PickupboyAdmin)




class OrderAdmin(admin.ModelAdmin):
    # inlines=(ShipmentInline,)
    #actions_on_top = True
    save_as = True
    list_per_page = 25
    search_fields = ['user__phone', 'name', 'namemail__name', 'namemail__email', 'promocode__code', 'shipment__real_tracking_no','shipment__mapped_tracking_no','shipment__barcode','shipment__drop_phone','shipment__drop_name']
    list_display = (
        'order_no', 'book_time', 'promocode', 'date', 'time', 'full_address', 'name_email', 'order_status','mapped_ok', 'way',
        'pb', 'comment', 'shipments', 'send_invoice', 'warehouse')
    list_editable = ('date', 'time', 'order_status', 'pb', 'comment', 'warehouse')
    list_filter = ['book_time', 'status', 'pb','order_status', 'warehouse']
    raw_id_fields = ('pb', 'warehouse', )
    readonly_fields = ('code', 'send_invoice',)
    '''
	fieldsets=(
	('Basic Information', {'fields':['contact_number',('name','email'),'item_details',('date','time'),'code',],}),
	('Address', {'fields':['flat_no','address','pincode',],}),
	('Destination Address', {'fields':[('drop_name','drop_phone'),'drop_flat_no','locality',('city','state'),('drop_pincode','country')] ,})
			#('Invoices',{'fields':['send_invoice'], 'classes':('suit-tab','suit-tab-invoices')})
	)
	'''  # passing variables to change_list view

    def mapped_ok(self,obj):
        products=Shipment.objects.filter(order=obj)
        mapped_ok=True
        for product in products:
            if (not product.mapped_tracking_no):
                return False
        return mapped_ok
    mapped_ok.boolean = True

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        cs=False
        op=False
        try:
            print "jkjkjkjkjkjkjkjkjkjk"
            print "see"
            profile=Profile.objects.get(user=request.user)
            usertype=profile.usertype
            if (usertype=='C'):
                print "jkjkjkjkjkjkjkjkjkjk"
                cs=True
            if (usertype=='O'):
                op=True
        except:
            pass

        todays_date = date.today()

        today_min = datetime.datetime.combine(todays_date, datetime.time.min)
        today_max = datetime.datetime.combine(todays_date, datetime.time.max)

        o = Order.objects.filter(order_status='O').count()
        a = Order.objects.filter(order_status='A').count()
        p = Order.objects.filter(order_status='P').count()
        pa = Order.objects.filter(order_status='AP').count()
        c = Order.objects.filter(order_status='DI').count()
        completed = Order.objects.filter(order_status='C').count()
        acs= Order.objects.filter().exclude(order_status='O').exclude(order_status='N').count()
        todays_date = date.today()
        # week_before=date.today()-datetime.timedelta(days=7)

        # today min/max
        today_min = datetime.datetime.combine(todays_date, datetime.time.min)
        today_max = datetime.datetime.combine(todays_date, datetime.time.max)

        #week min/max
        #	date_min = datetime.datetime.combine(week_before, datetime.time.min)
        #	date_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)

        #customer stats today

        today_orders = Order.objects.filter(Q(book_time__range=(today_min, today_max)))
        today_shipments_correct = Shipment.objects.filter(order=today_orders).exclude(price__isnull=True).exclude(
            price__exact='')
        today_shipments = Shipment.objects.filter(order=today_orders)
        average_b2c = today_shipments_correct.aggregate(Avg('price'))['price__avg']
        sum_b2c = today_shipments_correct.aggregate(Sum('price'))['price__sum']
        count_b2c = today_shipments.count()
        action_b2c = today_shipments.count() - today_shipments_correct.count()

        context = {'o': o, 'a': a, 'p': p, 'c': c, 'pa': pa, 'count_b2c': count_b2c, 'sum_b2c': sum_b2c,'cs':cs,'op':op,'acs':acs,'completed':completed}
        return super(OrderAdmin, self).changelist_view(request, extra_context=context)


    def get_fieldsets(self, request, obj=None):
        # Add 'item_type' on add forms and remove it on changeforms.
        if not obj:  # this is an add form
            fieldsets = (
                ('Basic Information',
                 {'fields': ['contact_number', ('name', 'email'), 'item_details', ('date', 'time'), 'code', ], }),
                ('Address', {'fields': ['flat_no', 'address', 'pincode', ], }),
                ('Destination Address', {
                    'fields': [('drop_name', 'drop_phone'), 'drop_flat_no', 'locality', ('city', 'state'),
                               ('drop_pincode', 'country')], })
                # ('Invoices',{'fields':['send_invoice'], 'classes':('suit-tab','suit-tab-invoices')})
            )

        else:  # this is a change form
            fieldsets = super(OrderAdmin, self).get_fieldsets(request, obj)

        return fieldsets


    def get_form(self, request, obj=None, **kwargs):
        if obj:  # obj is not None, so this is a change page
            # kwargs['exclude'] = ['owner']
            #print "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            #print self.__dict__
            #fieldsets=(
            #('Address', {'fields':['flat_no','address','pincode',],}),
            #)
            self.form = OrderEditForm

            self.fields = ['pincode', 'flat_no', 'address']
        else:  # obj is None, so this is an add page
            # kwargs['fields'] = ['id', 'family_name', 'status']
            #self.fields = ['id', 'family_name', 'status']
            #print "bbbbbbbbbbbbbbbbb"
            self.form = OrderForm
        # self.fields = ['pincode', 'flat_no']

        return super(OrderAdmin, self).get_form(request, obj, **kwargs)


    def suit_row_attributes(self, obj, request):
        print obj.name
        css_class = {
            'N': 'success',
            'C': 'warning',
            'P': 'error',
            'F': 'info',
        }.get(obj.status)
        if css_class:
            return {'class': css_class, 'data': obj.name}


    # actions = [make_pending,make_complete]
    def full_address(self, obj):
        return str(obj.flat_no) + ' ' + str(obj.address) + ' ' + str(
            obj.pincode) + '  <a href="/admin/myapp/order/%s/">edit address</a>' % (obj.pk)

    full_address.allow_tags = True

    def code(self, obj):
        try:
            code = obj.promocode.code
            return '<div style="color:red">%s</div>' % (code)
        except:
            return "no code"

    code.allow_tags = True

    def send_invoice(self, obj):
        valid = 1
        e_string = ''
        invoice_dict = {}
        total = 0
        order_no = obj.order_no
        invoice_dict['orderno'] = order_no

        try:
            times = Invoicesent.objects.filter(order=obj.order_no)
            times_count = str(times.count()) + ' invoices sent'
        except:
            times_count = "0 invoices sent"

        try:
            name = obj.namemail.name
            invoice_dict['name'] = name
        except:
            e_string = e_string + 'name not set <br>'
            valid = 0

        try:
            address = obj.address
            invoice_dict['address'] = address
        except:
            e_string = e_string + 'address not set <br>'
            valid = 0

        try:
            email = obj.namemail.email
            invoice_dict['mailto'] = email
        except:
            e_string = e_string + 'email not set <br>'

        try:
            book_time = obj.book_time
            invoice_dict['date'] = str(book_time)[0:10]
        except:
            e_string = e_string + 'time not set <br>'

        try:
            shipments = Shipment.objects.filter(order=obj.order_no)
            number = shipments.count()
            invoice_dict['numberofshipment'] = number
            count = 0
            total = 0
            for s in shipments:
                try:

                    print s.real_tracking_no
                    print s.drop_address.pincode
                    print s.weight
                    print 'check'

                    if s.weight is None or s.weight.strip() == '':
                        e_string = e_string + str(s.real_tracking_no) + ' weight not set <br>'
                        valid = 0
                    if s.drop_address.pincode is None:
                        e_string = e_string + str(s.real_tracking_no) + ' drop_address pincode not set <br>'
                        valid = 0
                    if s.price is None or s.price.strip() == '':
                        e_string = e_string + str(s.real_tracking_no) + ' price not set <br>'
                        valid = 0

                    try:
                        invoice_dict['des' + str(count)] = str(s.weight) + ' kg to ' + str(s.drop_address.pincode)
                        invoice_dict['tracking' + str(count)] = str(s.real_tracking_no)
                        invoice_dict['price' + str(count)] = str(s.price)
                        invoice_dict['total' + str(count)] = str(s.price)
                        invoice_dict['quantity' + str(count)] = '1'
                        total = total + int(s.price)
                    except Exception, e:
                        print str(e)

                    count = count + 1
                except Exception, e:
                    print str(e)
                    e_string = e_string + 'error in fetching shipments <br>'
                    valid = 0

                invoice_dict['overalltotal'] = total


        except:
            e_string = e_string + 'number of xx shipments not set <br>'
            valid = 0




        #			address=obj.address
        #			shipments = Shipment.objects.filter(order=obj.order_no)
        #			mail_subject="a"
        #			mail_content="ggh"
        if (valid):
            return '%s <br> <a target="_blank" href="http://128.199.210.166/payment_invoice.php?%s">generate  and send invoice to %s</a>' % (
                times_count, urllib.urlencode(invoice_dict), invoice_dict['mailto'])
        else:
            return e_string

    send_invoice.allow_tags = True



    #http://128.199.210.166/test1.php?name=sargun&address=119%2C+nehru+park&orderno=123&date=12%2F12%2F12&mailto=sargungu%40gmail.com&numberofshipment=1&des0=5+kg+to+400076&des1=1+kg+to+456006&des2=&tracking0=S123433&tracking1=S342423&tracking2=&price0=12&price1=12&price2=&quantity0=1&quantity1=1&quantity2=&total0=12&total1=12&total2=&overalltotal=24&discount=&submit=Submit

    def name_email(self, obj):
        #pk=obj.namemail.pk
        try:
            user = obj.user
            pk = obj.namemail.pk
            name = obj.namemail.name
            email = obj.namemail.email

            #approvedordercs/?q=8879006197

            return '%s<br><a href ="/admin/myapp/approvedordercs/?q=%s" target="_blank" >(click here for previous order history)</a><br> <br><br><a href="/admin/myapp/namemail/%s/" onclick="return showAddAnotherPopup(this);">%s|%s</a>' % (
                user,user, pk, name, email)
        except:
            return 'fail'

    name_email.allow_tags = True


    def shipments(self, obj):
        shipments = Shipment.objects.filter(order=obj.order_no)
        i = 0
        output = ''
        for x in shipments:
            output = output + '<a href ="/admin/myapp/shipment/' + str(
                x.pk) + '/" target="_blank" >' + str(x.real_tracking_no) + '</a> <br>'
        return output

    shipments.allow_tags = True  # <img src="https://farm8.staticflickr.com/7042/6873010155_d4160a32a2_s.jpg" onmouseover="this.width='500'; this.height='500'" onmouseout="this.width='100'; this.height='100'">

admin.site.register(Order, OrderAdmin)
admin.site.register(Gcmmessage)
admin.site.register(Promocode)


class CSOrderAdmin(OrderAdmin):
    list_display = (
        'order_no', 'book_time', 'promocode', 'date', 'time', 'full_address', 'name_email', 'order_status','mapped_ok', 'way',
        'cs_comment', 'shipments')
    list_editable = ('date', 'time', 'order_status', 'cs_comment',)


class OPOrderAdmin(OrderAdmin):
    list_display = (
        'order_no', 'warehouse', 'book_time', 'promocode', 'date', 'time', 'full_address', 'name_email', 'order_status','pb', 'mapped_ok','way',
        'cs_comment','comment', 'shipments')
    list_editable = ('pb', 'warehouse', 'order_status','comment',)




class PromocheckAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('code', 'user')


admin.site.register(Promocheck, PromocheckAdmin)


def make_alloted(modeladmin, request, queryset):
    queryset.update(order_status='A')


make_alloted.short_description = "Mark selected orders as alloted"


class ReceivedOrderAdmin(CSOrderAdmin):
    def make_approved(modeladmin, request, queryset):
        queryset.update(order_status='AP')

    def make_cancelled(modeladmin, request, queryset):
        queryset.update(order_status='N')


    make_approved.short_description = "Approve"
    make_cancelled.short_description = "Cancel"

    actions = [make_approved,make_cancelled]


    def queryset(self, request):
        return self.model.objects.filter(order_status='O')


admin.site.register(ReceivedOrder, ReceivedOrderAdmin)


def make_pickedup(modeladmin, request, queryset):
    queryset.update(order_status='P')


make_alloted.short_description = "Mark selected orders as picked up"


class AllotedOrderAdmin(OPOrderAdmin):
    def make_pickedup(modeladmin, request, queryset):
        queryset.update(order_status='P')


    make_alloted.short_description = "picked up"

    actions = [make_pickedup]

    def queryset(self, request):
        return self.model.objects.filter(order_status='A')


admin.site.register(AllotedOrder, AllotedOrderAdmin)


class DispatchedOrderAdmin(OPOrderAdmin):
    
    def queryset(self, request):
        return self.model.objects.filter(order_status='DI')


admin.site.register(DispatchedOrder, DispatchedOrderAdmin)



class PickedupOrderAdmin(OPOrderAdmin):
    def make_dispatched(modeladmin, request, queryset):
        queryset.update(order_status='DI')


    make_alloted.short_description = "dispatched"

    actions = [make_dispatched]

    def queryset(self, request):
        return self.model.objects.filter(order_status='P')


admin.site.register(PickedupOrder, PickedupOrderAdmin)




class ApprovedOrderAdmin(OPOrderAdmin):
    def make_Alloted(modeladmin, request, queryset):
        queryset.update(order_status='A')


    make_alloted.short_description = "Alloted"

    actions = [make_alloted]

    def queryset(self, request):
        return self.model.objects.filter(order_status='AP').order_by('time')


admin.site.register(ApprovedOrder, ApprovedOrderAdmin)

class ApprovedOrderCsAdmin(CSOrderAdmin):

    def queryset(self, request):
        return self.model.objects.filter().exclude(order_status='O').exclude(order_status='N').exclude(order_status='F')

admin.site.register(ApprovedOrderCs, ApprovedOrderCsAdmin)


class CompletedOrderAdmin(OrderAdmin):
    def queryset(self, request):
        return self.model.objects.filter(order_status='C')


admin.site.register(CompletedOrder, CompletedOrderAdmin)


class CancelledOrderAdmin(CSOrderAdmin):
    def queryset(self, request):
        return self.model.objects.filter(order_status='N')


admin.site.register(CancelledOrder, CancelledOrderAdmin)


class FakeOrderAdmin(OrderAdmin):
    def queryset(self, request):
        return self.model.objects.filter(order_status='F')


admin.site.register(FakeOrder, FakeOrderAdmin)


class QueryOrderAdmin(OrderAdmin):
    def queryset(self, request):
        return self.model.objects.filter(order_status='Q')


admin.site.register(QueryOrder, QueryOrderAdmin)


class ShipmentAdmin(admin.ModelAdmin):
    list_per_page = 10
    form = ShipmentForm

    search_fields = ['order__order_no', 'real_tracking_no', 'mapped_tracking_no', 'drop_phone', 'drop_name']
    list_display = (
        'real_tracking_no', 'name', 'cost_of_courier', 'weight', 'mapped_tracking_no', 'company', 'parcel_details',
        'price',
        'category', 'drop_phone', 'drop_name', 'status', 'address', 'print_invoice', 'generate_order', 'fedex','barcode', 'img',)
    list_filter = ['category','last_tracking_status']
    list_editable = (
        'name', 'cost_of_courier', 'weight', 'mapped_tracking_no', 'company', 'price', 'category', 'drop_phone',
        'drop_name', 'barcode', 'img',)
    readonly_fields = ('real_tracking_no', 'print_invoice', 'generate_order', 'fedex','parcel_details', 'address', 'fedex')

    fieldsets = (
        ('Basic Information', {'fields': ['real_tracking_no', 'parcel_details', ('category', 'status')],
                               'classes': ('suit-tab', 'suit-tab-general')}),
        ('Parcel Information',
         {'fields': [('name', 'weight', 'cost_of_courier'), ], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Amount paid', {'fields': ['price', ], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Tracking Information',
         {'fields': [('mapped_tracking_no', 'company'), 'kartrocket_order'], 'classes': ('suit-tab', 'suit-tab-general')}),
        #('Destination Address', {'fields':['drop_name','drop_phone','drop_flat_no','locality','city','state','drop_pincode','country'] , 'classes':['collapse',]})
        ('Destination Address',
         {'fields': [('drop_name', 'drop_phone'), 'address', ], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Actions', {'fields': ['print_invoice', 'generate_order', 'fedex'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Tracking', {'fields': ['tracking_data','tracking_history'], 'classes': ('suit-tab', 'suit-tab-tracking')})
    )

    suit_form_tabs = (('general', 'General'), ('tracking', 'Tracking'))


    def response_change(self, request, obj):

        #print self.__dict__
        #print request.__dict__
        #print obj.pk
        print "sdddddddddddddddddddddddddddd"
        #return super(UserAdmin, self).response_change(request, obj)

        

        return HttpResponseRedirect(request.build_absolute_uri('/admin/myapp/shipment/'+ str(obj.pk) + '/'))

    def address(self, obj):
        try:
            address = obj.drop_address
            pk = address.pk
            add = str(address.flat_no) + ',' + str(address.locality) + ',' + str(address.city) + ',' + str(
                address.state) + '-' + str(address.pincode)
            return '<a href="/admin/myapp/address/%s/" onclick="return showAddAnotherPopup(this);">%s</a>' % (pk, add)
        except:
            return "no add"

    address.allow_tags = True

    def print_invoice(self, obj):
        valid = 1
        e_string = ''
        invoice_dict = {}
        #total=0
        try:
            order_no = obj.order.order_no
            invoice_dict['orderno'] = order_no
        except:
            e_string = e_string + 'order_no not set <br>'
            valid = 0

        try:
            name = obj.order.namemail.name
            invoice_dict['name'] = name
        except:
            e_string = e_string + 'name not set <br>'
            valid = 0

        try:

            address = str(obj.order.flat_no) + ' ' + str(obj.order.address) + ', ' + str(obj.order.pincode)
            invoice_dict['address'] = address
            invoice_dict['time'] = str(obj.order.date) + ': ' + str(obj.order.time)
            invoice_dict['phone'] = str(obj.order.user.phone)
        #invoice_dict['code']=str(obj.order.promocode.code)

        except:
            e_string = e_string + 'address not set <br>'
            valid = 0

        try:
            invoice_dict['code'] = str(obj.order.promocode.code)
        except:
            invoice_dict['code'] = "No promocode"

        try:
            name2 = str(obj.drop_name)
            invoice_dict['name2'] = name2
            invoice_dict['phone2'] = str(obj.drop_phone)

        except:
            e_string = e_string + 'drop_name not set <br>'

        try:
            address2 = obj.drop_address
            if (str(address2) == 'None,None,None,None,None,None'):
                invoice_dict['address2'] = " "
            else:
                invoice_dict['address2'] = address2
        except:
            e_string = e_string + 'drop_address not set <br>'

        try:
            book_time = obj.order.book_time
            invoice_dict['date'] = str(book_time)[0:10]
        except:
            e_string = e_string + 'time not set <br>'

        try:
            invoice_dict['tracking'] = str(obj.real_tracking_no)

        except:
            e_string = e_string + 'number of xx shipments not set <br>'
            valid = 0




        #			address=obj.address
        #			shipments = Shipment.objects.filter(order=obj.order_no)
        #			mail_subject="a"
        #			mail_content="ggh"
        if (valid):
            return '<a target="_blank" href="http://128.199.210.166/customer_label.php?%s">generate pdf</a>' % (
                urllib.urlencode(invoice_dict))
        else:
            return e_string

    print_invoice.allow_tags = True

    def parcel_details(self, obj):
        name = str(obj.img)
        print name
        if (name == ''):
            return str(obj.item_name)
        name_mod = name[9:]
        full_url = 'http://128.199.159.90/static/' + name_mod
        return '<img src="%s" width=60 height=60 onmouseover="this.width=\'500\'; this.height=\'500\'" onmouseout="this.width=\'100\'; this.height=\'100\'" />' % (
            full_url)

    parcel_details.allow_tags = True


    def generate_order(self, obj):

        valid = 1
        try:
            string = ''
            shipment = Shipment.objects.get(pk=obj.pk)
            address = shipment.drop_address
            error_string = ''
            try:
                orderid = shipment.pk
                string = string + 'orderid=' + str(orderid) + '&'
            except:
                valid = 0
                error_string = error_string + 'orderid not set <br>'

            try:
                shipmentid = shipment.real_tracking_no
                string = string + 'shipmentid=' + str(shipmentid) + '&'
            except:
                valid = 0
                error_string = error_string + 'shipmentid not set <br>'

            try:
                name = shipment.drop_name
                if (str(name) != ''):
                    string = string + 'name=' + str(name) + '&'
                else:
                    error_string = error_string + 'drop_name not set<br>'
                    valid = 0

            except:
                valid = 0
                error_string = error_string + 'drop_name not set<br>'

            try:
                pname = shipment.name
                if (str(pname) != ''):
                    string = string + 'pname=' + str(pname) + '&'
                else:
                    error_string = error_string + 'item_name not set<br>'
                    valid = 0
            except:
                error_string = error_string + 'item_name not set<br>'
                valid = 0

            try:
                price = shipment.cost_of_courier

                if (str(price) != '' and str(price) != 'None'):
                    string = string + 'price=' + str(price) + '&'
                else:
                    error_string = error_string + 'item_cost not set<br>'
                    valid = 0
            except:
                error_string = error_string + 'item_cost not set<br>'
                valid = 0

            try:
                weight = shipment.weight
                if (str(weight) != '' and str(weight) != 'None'):
                    string = string + 'weight=' + str(weight) + '&'
                else:
                    error_string = error_string + 'item_weight not set<br>'
                    valid = 0

            except:
                error_string = error_string + 'item_weight not set<br>'
                valid = 0

            try:
                phone = shipment.drop_phone
                if (str(phone) != '' and str(phone) != 'None'):
                    string = string + 'phone=' + str(phone) + '&'
                else:
                    error_string = error_string + 'drop_phone not set<br>'
                    valid = 0
            except:
                error_string = error_string + 'drop_phone not set<br>'
                valid = 0

            try:
                address1 = str(address.flat_no) + str(address.locality)
                string = string + 'address=' + str(address1) + '&'
            except:
                error_string = error_string + 'address not set<br>'
                valid = 0

            try:
                city = address.city
                string = string + 'city=' + str(city) + '&'
            except:
                error_string = error_string + 'city not set<br>'
                valid = 0

            try:
                state = address.state
                string = string + 'state=' + str(state) + '&'
            except:
                error_string = error_string + 'state not set<br>'
                valid = 0

            try:
                pincode = address.pincode
                string = string + 'pincode=' + str(pincode) + '&'
            except:
                error_string = error_string + 'pincode not set<br>'
                valid = 0

        except:
            pass

        if (valid):
            return 'All good!<br><a href="http://order.sendmates.com/?%s" target="_blank" >Create Normal Order</a> <br> <a href="http://order.sendmates.com/cod/?%s" target="_blank" >Create Cod Order</a>' % (
                string, string)
        else:
            return '<div style="color:red">' + error_string + '</div>'

    generate_order.allow_tags = True

    def fedex(self, obj):
        params = urllib.urlencode({'shipment_pk': obj.pk, 'client_type': "customer"})

        if not obj.drop_address.state:
            return "Enter state"

        if not state_matcher.is_state(obj.drop_address.state):
            return '<h2 style="color:red">Enter a valid state</h2>'

        if not obj.drop_address.pincode:
            return "Enter pincode"

        db_pincode = Pincode.objects.filter(pincode=obj.drop_address.pincode)

        if db_pincode:
            if not db_pincode[0].fedex_servicable:
                return '<h2 style="color:red">Not Servicable</h2>'
            elif db_pincode[0].fedex_oda_opa:
                return '<h2 style="color:red">ODA</h2>'
        else:
            return '<h2 style="color:red">Enter a valid pincode</h2>'

        if not obj.weight:
            return "Enter applied weight"

        if not obj.cost_of_courier:
            return "Enter item value"

        if obj.drop_address.state == 'Kerala' and obj.category == 'E':
            return '<h2 style="color:red">Not Servicable</h2>'

        if obj.drop_address.state == 'West Bengal' and float(obj.cost_of_courier) > 1000:
            return '<h2 style="color:red">Not Servicable</h2>'

        if obj.fedex_outbound_label:
            if obj.drop_address.state == 'Gujarat' and obj.category == 'E':
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label") + '<br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order") + '<br><br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
            else:
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label") + '<br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order")

        if obj.drop_address.state == 'Gujarat' and obj.category == 'E':
            return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<br> <br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"

        if state_matcher.is_restricted(obj.drop_address.state) and not obj.is_document:
            return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<br> <h2 style="color:red">Restricted States</h2>'

        return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order")
    fedex.allow_tags = True


admin.site.register(Shipment, ShipmentAdmin)


class ZipcodeAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'city', 'state', 'zone', 'cod', 'fedex', 'aramex', 'delhivery', 'ecom', 'firstflight')
    search_fields = ['pincode']


admin.site.register(Zipcode, ZipcodeAdmin)


class XAdmin(admin.ModelAdmin):
    list_display = ('Name', 'C', 'thumbnail')

    def thumbnail(self, obj):
        name = str(obj.C)
        name_mod = name[9:]
        full_url = 'http://128.199.159.90/static/' + name_mod
        return '<img src="%s" width=60 height=60 />' % (full_url)

    thumbnail.allow_tags = True


admin.site.register(X, XAdmin)

admin.site.register(Forgotpass)


class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ('time', 'success', 'user')
    list_filter = ['time']


admin.site.register(LoginSession, LoginSessionAdmin)


class WeborderAdmin(admin.ModelAdmin):
    list_display = ('item_details', 'pickup_location', 'pincode', 'number', 'time')


admin.site.register(Weborder, WeborderAdmin)

admin.site.register(Priceapp)


class QcShipmentAdmin(ShipmentAdmin):
    
    def queryset(self, request):
        return self.model.objects.filter(Q(order__order_status='DI')| Q(order__order_status='R')).exclude(status='C')
    

    readonly_fields = ('category','drop_phone', 'drop_name','address','barcode','parcel_details','real_tracking_no','name','weight','cost_of_courier','price')
     
    list_display = (
        'order','tracking_nos','company','book_time','dispatch_time','customer_details','drop_name','drop_phone', 'tracking_status','last_location' ,'expected_delivery_date','last_updated','last_tracking_status','qc_comment')
    #list_filter = ['order__method','order__business']
    list_editable = ('qc_comment',)
# readonly_fields = ('order__method','drop_phone', 'drop_name', 'status', 'address','barcode','tracking_data','real_tracking_no','name','weight','cost_of_courier','price')
    search_fields = ['order__order_no', 'real_tracking_no', 'mapped_tracking_no', 'drop_phone', 'drop_name','tracking_data']
    list_filter=('company','last_tracking_status','warning','company')

    fieldsets = (
    ('Basic Information', {'fields': ['real_tracking_no', 'parcel_details', ('category', 'status')],
    'classes': ('suit-tab', 'suit-tab-general')}),
    ('Parcel Information',
    {'fields': [('name', 'weight', 'cost_of_courier'), ], 'classes': ('suit-tab', 'suit-tab-general')}),
    ('Amount paid', {'fields': ['price', ], 'classes': ('suit-tab', 'suit-tab-general')}),
    ('Tracking Information',
    {'fields': [('mapped_tracking_no', 'company'), 'kartrocket_order'], 'classes': ('suit-tab', 'suit-tab-general')}),
    #('Destination Address', {'fields':['drop_name','drop_phone','drop_flat_no','locality','city','state','drop_pincode','country'] , 'classes':['collapse',]})
    ('Destination Address',
    {'fields': [('drop_name', 'drop_phone'), 'address', ], 'classes': ('suit-tab', 'suit-tab-general')}),
    ('Tracking', {'fields': ['tracking_data'], 'classes': ('suit-tab', 'suit-tab-tracking')})
    )
    suit_form_tabs = (('general', 'General'), ('tracking', 'Tracking'))
    
    def tracking_status(self, obj):
    #pk=obj.namemail.pk
        return json.loads(obj.tracking_data)[-1]['status']
    tracking_status.allow_tags = True
    tracking_status.admin_order_field = 'tracking_data'

    def tracking_nos(self, obj):
        if (obj.company=='B'):
            return '<a href="http://www.bluedart.com/servlet/RoutingServlet?handler=tnt&action=awbquery&awb=awb&numbers=%s" target="_blank">%s</a>' % (obj.mapped_tracking_no, obj.mapped_tracking_no)
        elif (obj.company=='F'):
            return '<a href="https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber=%s" target="_blank">%s</a>' % (obj.mapped_tracking_no, obj.mapped_tracking_no)
        else:
            return obj.mapped_tracking_no
    tracking_nos.admin_order_field = 'mapped_tracking_no' #Allows column order sorting
    tracking_nos.allow_tags=True

    def last_location(self, obj):
#pk=obj.namemail.pk
        return json.loads(obj.tracking_data)[-1]['location']
    last_location.allow_tags = True
    last_location.admin_order_field = 'tracking_data'

    def customer_details(self, obj):
#pk=obj.namemail.pk
        return str (obj.order.namemail.name) + '<br>'+str(obj.order.user)+ '<br>'+str (obj.order.namemail.email) 
    customer_details.allow_tags = True

    def book_time(self, obj):
#pk=obj.namemail.pk
        fmt = '%B.%d,%Y %H:%M'
        return obj.order.book_time.replace(second=0, microsecond=0,tzinfo=None).strftime(fmt)
    book_time.allow_tags = True
    book_time.admin_order_field = 'order__book_time'

    def expected_delivery_date(self,obj):
        if (obj.category=='E'):
            return obj.order.book_time + timedelta(days=6)
        else:
            return obj.order.book_time + timedelta(days=3)
    expected_delivery_date.short_description='expected delivery date'
    expected_delivery_date.admin_order_field = 'order__book_time'


    def last_updated(self,obj):
        import datetime
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.datetime.now(z)
        time = ind_time.strftime(fmt)
        z = timezone('Asia/Kolkata')
        #fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.datetime.now(z)
        try:
            diff_time=ind_time.replace(second=0, microsecond=0,tzinfo=None)-obj.update_time.replace(second=0, microsecond=0,tzinfo=None)
            total_seconds = int(diff_time.total_seconds())
            hours, remainder = divmod(total_seconds,60*60)
            minutes, seconds = divmod(remainder,60)
            if (hours<24):
                return '%s hours,%s mins' %(hours, minutes)
            else:
                return '%s days %s hours,%s mins' %(hours/24,hours%24, minutes)
        except:
            return '-'
    last_updated.admin_order_field='update_time'

    def suit_row_attributes(self, obj, request):
        css_class = {False: 'success',True: 'error',}.get(obj.warning)
        if css_class:
            return {'class': css_class, 'data': obj.name}

admin.site.register(QcShipment, QcShipmentAdmin)