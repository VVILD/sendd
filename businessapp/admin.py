import urllib
import json



from datetime import date


from django.contrib import admin
from .models import *

from django.http import HttpResponse, HttpResponseRedirect

from django.db.models import Sum
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

import csv
from django.http import HttpResponse
from setuptools.compat import unicode



def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """

    from itertools import chain

    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/2369/
        """
        opts = modeladmin.model._meta
        field_names = set([field.name for field in opts.fields])
        many_to_many_field_names = set([many_to_many_field.name for many_to_many_field in opts.many_to_many])
        if fields:
            fieldset = set(fields)
            field_names = field_names & fieldset
        elif exclude:
            excludeset = set(exclude)
            field_names = field_names - excludeset

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csv.writer(response)
        if header:
            writer.writerow(list(chain(field_names, many_to_many_field_names)))
        for obj in queryset:
            row = []
            for field in field_names:
                row.append(unicode(getattr(obj, field)))
            for field in many_to_many_field_names:
                row.append(unicode(getattr(obj, field).all()))

            writer.writerow(row)
        return response
    export_as_csv.short_description = description
    return export_as_csv

# Register your models here.
class BusinessAdmin(admin.ModelAdmin):
    # search_fields=['name']
    search_fields=['username','business_name']
    list_display = ('username', 'business_name', 'pickup_time', 'pb', 'assigned_pickup_time','status', 'pending_orders','pickedup_orders','daily','comment')
    list_editable = ('pb', 'assigned_pickup_time','daily','comment')
    raw_id_fields = ('pb',)
    list_filter = ['username', 'status', 'daily','pb']

    def pending_orders(self, obj):
        po_count = Order.objects.filter(status='P', business__username=obj.username).count()
        return '<a href="/admin/businessapp/order/?q=&business__username__exact=%s&status__exact=P"> %s </a>' % (
            obj.username, po_count)

    pending_orders.allow_tags = True
    def pickedup_orders(self, obj):
        po_count = Order.objects.filter(status='PU', business__username=obj.username).count()
        return '<a href="/admin/businessapp/order/?q=&business__username__exact=%s&status__exact=PU"> %s </a>' % (obj.username, po_count)
    pickedup_orders.allow_tags = True

    def pending_orders_today(self, obj):
        todays_date=date.today()
        date_max = datetime.datetime.combine(todays_date, datetime.time.max)
        date_min = datetime.datetime.combine(todays_date, datetime.time.min)
        po_count = Order.objects.filter(book_time__range=(date_min,date_max),status='P', business__username=obj.username).count()
        return '<a href="/admin/businessapp/order/?q=&business__username__exact=%s&status__exact=P"> %s </a>' % (obj.username, po_count)
    pending_orders_today.allow_tags = True

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


def make_complete(modeladmin, request, queryset):
    queryset.update(status='C')


make_complete.short_description = "Mark selected orders as Complete"


def make_transit(modeladmin, request, queryset):
    queryset.update(status='D')


make_complete.short_description = "Mark selected orders as In Transit"


def make_pending(modeladmin, request, queryset):
    queryset.update(status='P')


make_pending.short_description = "Mark selected orders as Pending"


def make_cancelled(modeladmin, request, queryset):
    queryset.update(status='N')


make_cancelled.short_description = "Mark selected orders as Cancelled"

from django.forms import ModelForm, Textarea, HiddenInput
from django import forms
from businessapp.models import Product, Order


# class BmInline(admin.StackedInline):
# model = BusinessManager
# can_delete = False
#     verbose_name_plural = 'businessmanager'

# Define a new User admin
# class UserAdmin(UserAdmin):
# inlines = (BmInline, )

# Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)


class ProductForm(ModelForm):
    class Meta:
        model = Product
        widgets = {
            'tracking_data': HiddenInput,
            'date': HiddenInput,
        }


admin.site.register(X)

admin.site.register(Business, BusinessAdmin)

admin.site.register(LoginSession)


class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name', 'real_tracking_no']
    list_display = ('name', 'price', 'weight', 'status', 'fedex_check', 'real_tracking_no', 'order', 'barcode','date',)
    list_editable = ('status', )
    list_filter=['order__business']
    readonly_fields = (
        'name', 'quantity', 'sku', 'price', 'weight', 'applied_weight', 'real_tracking_no', 'order',
        'kartrocket_order', 'shipping_cost', 'cod_cost', 'status', 'date', 'fedex_check','barcode')


    fieldsets = (
        ('Tracking_details', {'fields': ['mapped_tracking_no', 'company','real_tracking_no','kartrocket_order'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('General', {'fields': ['name', 'quantity','sku','price','weight','applied_weight','status','date','remittance','order'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Cost', {'fields': ['shipping_cost', 'cod_cost','return_cost'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Tracking', {'fields': ['tracking_data'], 'classes': ('suit-tab', 'suit-tab-tracking')}),
        ('Barcode', {'fields': ['barcode'], 'classes': ('suit-tab', 'suit-tab-barcode')}),
    )

    suit_form_tabs = (('general', 'General'), ('tracking', 'Tracking'),('barcode', 'Barcode'))

    actions = [export_as_csv_action("CSV Export", fields=['name','real_tracking_no','order__name'])]

admin.site.register(Product, ProductAdmin)

admin.site.register(Payment)
admin.site.register(Forgotpass)

class PricingAdmin(admin.ModelAdmin):
    # search_fields=['name']
    list_filter=('business__username','business__business_name')


admin.site.register(Pricing,PricingAdmin)

# admin.site.register(BusinessManager)


# name = models.CharField(max_length = 100,null=True,blank =True)
# quantity = models.IntegerField(max_length = 10,null=True,blank =True)
# sku = models.CharField(max_length = 100,null=True,blank =True)
# price = models.IntegerField(max_length = 10,null=True,blank =True)
# weight = models.IntegerField(max_length = 10,null=True,blank =True)
# applied_weight = models.IntegerField(max_length = 10,null=True,blank =True)
# order=models.ForeignKey(Order,null=True,blank =True)
# real_tracking_no=models.CharField(max_length=10,blank=True,null=True)
# mapped_tracking_no=models.CharField(max_length = 50,null=True,blank=True)
# tracking_data=models.CharField(max_length = 8000,null=True,blank=True)

# company=models.CharField(max_length=1,
# 								  choices=(('F','FedEx') ,('D','Delhivery'),),
# 								  blank=True , null = True)
# shipping_cost=models.IntegerField(null=True,blank=True)
# date=models.DateTimeField(null=True,blank=True)


class ProductInline(admin.TabularInline):
    model = Product
    form = ProductForm
    exclude = ['sku', 'weight', 'real_tracking_no', 'tracking_data']
    readonly_fields = ('product_info', 'weight', 'shipping_cost', 'generate_order', 'fedex',)
    fields = (
        'product_info', 'name', 'quantity', 'price', 'weight', 'applied_weight', 'generate_order', 'fedex')
    extra = 0

    def product_info(self, obj):
        return '<b>Name:</b>' + str(obj.name) + '<br>' + '<b>Quantity:</b>' + str(
            obj.quantity) + '<br>' + 'SKU: ' + str(obj.sku) + '<br>' + '<b>Price:</b>' + str(
            obj.price) + '<br>' + "<b>Fedex check:</b>" + str(
            obj.get_fedex_check_display()) + '<br>' + "<b>tracking_no:</b>" + str(
            obj.real_tracking_no) + '<br>' + "<b>kartrocket_order:</b>" + str(
            obj.kartrocket_order) + '<br>' + "<b>Mapped_tracking_no:</b>" + str(
            obj.mapped_tracking_no) + '<br>'+ "<b>status</b>" + str(
            obj.status) + '<br>' + "<b>company:</b>" + str(
            obj.company) + '<br>' + "<b>Shipping cost:</b>" + str(
            obj.shipping_cost) + '<br>' + "<b>Cod cost:</b>" + str(
            obj.cod_cost) + '<br>' + "<b>BARCODE:</b>" + str(
            obj.barcode) + '<br>'+ "<b> actual_shipping_cost :</b>" + str(
            obj.actual_shipping_cost) + '<br>'  + "<b><a href='%s%s/' target='_blank' >Product link (use this only when parcel is not sent via KARTROCKET):</b></a>" % (
            "/admin/businessapp/product/", obj.pk)

    product_info.allow_tags = True
    #'cod_cost'
    #'mapped_tracking_no', 'company' ,'shipping_cost',


    def generate_order(self, obj):
        #neworder=GCMDevice.objects.create(registration_id='fdgfdgfdsgfsfdg')
        #device = GCMDevice.objects.get(registration_id='APA91bGKEsBkDFeODXaS0coILc__0qPaWA6etPbK3fiWad2vluI_Q_EQVw9wocFgqCufbJy43PPXxhr7TB2QMx4QSHCgvBoq2l9dzxGRGX0Mnx6V9pPH2p2lAP93XZKyKjVWRu1PIvwd')
        #print "dsa"
        #devicorder.e.send_message("wadhwsdfdsa")
        #print device
        #device = GCMDevice.objects.get(registration_id='APA91bFT-KrRjrc6fWp8KPHDCATa5dgWCmCIARc_ESElyQ2yLKCoVVJAa477on0VtxDaZtvZCAdMerld7lLyr_TW3F3xoUUCqv1zmzr3JnVJrt5EvnoolR2p6J5pgC3ks4jF6o6_5ITE')
        #device.send_message("harsh bahut bada chakka hai.harsh", extra={"tracking_no": "S134807P31","url":"http://128.199.159.90/static/IMG_20150508_144433.jpeg"})
        #device.send_message("harsh bahut bada chakka hai.harsh")

        valid = 1
        try:
            string = ''
            product = Product.objects.get(pk=obj.pk)
            order = product.order
            print order
            error_string = ''
            try:
                shipmentid = product.real_tracking_no
                string = string + 'shipmentid=' + str(shipmentid) + '&'
            except:
                valid = 0
                error_string = error_string + 'shipmentid not set <br>'

            try:
                name = order.name
                if (str(name) != ''):
                    string = string + 'name=' + str(name) + '&'
                else:
                    error_string = error_string + 'drop_name not set<br>'
                    valid = 0

            except:
                valid = 0
                error_string = error_string + 'drop_name not set<br>'

            try:
                pname = product.name
                if (str(pname) != ''):
                    string = string + 'pname=' + str(pname) + '&'
                else:
                    error_string = error_string + 'item_name not set<br>'
                    valid = 0
            except:
                print 's'
                error_string = error_string + 'item_name not set<br>'
                valid = 0

            try:
                price = product.price

                if (str(price) != '' and str(price) != 'None'):
                    string = string + 'price=' + str(price) + '&'
                    print "jkjkjkjkjkjkjkjkjkjk"
                    print price
                    print "jkjkjkjkjkjkjkjkjkjk"
                else:
                    error_string = error_string + 'item_cost not set<br>'
                    valid = 0
            except:
                print 's'
                error_string = error_string + 'item_cost not set<br>'
                valid = 0

            try:
                weight = product.applied_weight
                if (str(weight) != '' and str(weight) != 'None'):
                    string = string + 'weight=' + str(weight) + '&'
                else:
                    error_string = error_string + 'item_weight not set<br>'
                    valid = 0

            except:
                print 's'
                error_string = error_string + 'item_weight not set<br>'
                valid = 0

            try:
                phone = order.phone
                if (str(phone) != '' and str(phone) != 'None'):
                    string = string + 'phone=' + str(phone) + '&'
                else:
                    error_string = error_string + 'drop_phone not set<br>'
                    valid = 0
            except:
                print 's'
                error_string = error_string + 'drop_phone not set<br>'
                valid = 0

            try:
                address1 = str(order.address1)
                string = string + 'address=' + str(address1) + '&'
            except:
                print 's'
                error_string = error_string + 'address 1 not set<br>'
                valid = 0

            try:
                address2 = str(order.address2)
                string = string + 'address1=' + str(address2) + '&'
            except:
                print 's'
                error_string = error_string + 'address 2 not set<br>'
                valid = 0

            try:
                city = order.city
                string = string + 'city=' + str(city) + '&'
            except:
                error_string = error_string + 'city not set<br>'
                valid = 0
                print 'k'

            try:
                state = order.state
                string = string + 'state=' + str(state) + '&'
            except:
                error_string = error_string + 'state not set<br>'
                valid = 0
                print 's'

            try:
                pincode = order.pincode
                string = string + 'pincode=' + str(pincode) + '&'
            except:
                error_string = error_string + 'pincode not set<br>'
                valid = 0
                print 's'



            #message="Hi " + user.name +", \n Greetings from DoorMint!,Our service provider ' "  + serviceprovider_name + "' (" + serviceprovider_number +") will reach you on "+book_date +" at "+str_time+" for "+ service1_name + "( "+service2_name+"). Call 9022662244, if you need help . Thanks for choosing us!"
            #message=urllib.quote(message)

        except:
            print 's'

        if (valid):
            return 'All good!<br><a href="http://order.sendmates.com/baindex.php?%s" target="_blank" >Create Normal Order</a> <br> <a href="http://order.sendmates.com/cod/?%s" target="_blank" >Create Cod Order</a>' % (
                string, string)
        else:
            return '<div style="color:red">' + error_string + '</div>'

    generate_order.allow_tags = True

    def fedex(self, obj):
        params = urllib.urlencode({'shipment_pk': obj.pk, 'client_type': "business"})
        if not obj.applied_weight:
            return "Enter applied weight"
        elif obj.fedex_check != 'P' and obj.fedex_check is not None and obj.fedex_check != 'R':
            return "Fedex Check Failed" + '<br> <h2 style="color:red">' + obj.get_fedex_check_display() + '</h2>'
        else:
            if obj.fedex_outbound_label and obj.fedex_cod_return_label:
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label")+'<br>'+ '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_cod_return_label.name).split('/')[-1], "Print COD Return Label") + '<br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order")
            elif obj.fedex_outbound_label:
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label") + '<br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order")
            else:
                if obj.fedex_check != 'R':
                    return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order")
                else:
                    return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<h2 style="color:red">Restricted States</h2>'

    fedex.allow_tags = True


# fieldsets=(
# ('Basic Information', {'fields':['real_tracking_no','print_invoice',], 'classes':('suit-tab','suit-tab-general')}),
# 	#('Address', {'fields':['flat_no','address','pincode',], 'classes':('suit-tab','suit-tab-general')}),
# 	#('Destination Address', {'fields':['drop_name','drop_phone','drop_flat_no','locality','city','state','drop_pincode','country'] , 'classes':['collapse',]})
# 	#('Invoices',{'fields':['send_invoice',], 'classes':('suit-tab','suit-tab-invoices')})
# )
# suit_form_tabs = (('general', 'General'))
class FilterUserAdmin(admin.ModelAdmin):


    def queryset(self, request):
        try:
            qs = super(FilterUserAdmin, self).queryset(request)
            print "queryyyset"

            profile=Profile.objects.get(user=request.user)

            if (profile.usertype!='B'):
                return qs.filter()
            else:
                return qs.filter(business__businessmanager__user=request.user)
        except:
            return qs.filter()


    def has_change_permission(self, request, obj=None):
        try:
            if not obj:
                # the changelist itself
                return True
            profile=Profile.objects.get(user=request.user)

            if (profile.usertype=='B'):

                return obj.business.businessmanager.user == request.user
            else:
                return True

        except:
            return True


    



class OrderAdmin(FilterUserAdmin):

    inlines = (ProductInline,)
    search_fields = ['business__business_name', 'name', 'product__real_tracking_no', 'product__barcode','city','state','product__mapped_tracking_no']
    list_display = (
        'order_no', 'book_time', 'business_details', 'name', 'status', 'fedex_check','mapped_ok', 'no_of_products', 'total_shipping_cost',
        'total_cod_cost', 'method',)
    list_editable = ('status',)
    list_filter = ['business', 'status', 'book_time']
    actions = [make_pending, make_complete, make_cancelled, make_transit,export_as_csv_action("CSV Export", fields=['name','product__real_tracking_no'])]


    def mapped_ok(self,obj):
        products=Product.objects.filter(order=obj)
        mapped_ok=True
        for product in products:
            if (not product.mapped_tracking_no):
                return False
        return mapped_ok
    mapped_ok.boolean = True


    def no_of_products(self, obj):
        return Product.objects.filter(order=obj).count()


    def total_cod_cost(self, obj):
        return Product.objects.filter(order=obj).aggregate(Sum('cod_cost'))['cod_cost__sum']

    def total_shipping_cost(self, obj):
        return Product.objects.filter(order=obj).aggregate(Sum('shipping_cost'))['shipping_cost__sum']


    def response_change(self, request, obj):
        #print self.__dict__
        #print request.__dict__
        #print obj.pk
        print "sdddddddddddddddddddddddddddd"
        #return super(UserAdmin, self).response_change(request, obj)
        return HttpResponseRedirect(request.build_absolute_uri('/admin/businessapp/order/' + str(obj.pk) + '/'))

    def suit_row_attributes(self, obj, request):
        css_class = {
            'N': 'success',
            'C': 'warning',
            'P': 'error',
            'F': 'info',
        }.get(obj.status)
        if css_class:
            return {'class': css_class, 'data': obj.name.encode('utf-8')}

    def business_details(self, obj):
        return '<a href="/admin/businessapp/business/%s/">%s</a>' % (obj.business.username, obj.business.business_name)

    def fedex_check(self, obj):
        status = 'Pass'
        products = Product.objects.filter(order=obj)
        for product in products:
            if product.fedex_check != 'P':
                status = product.get_fedex_check_display()
        return status

    business_details.allow_tags = True


'''
reference_id=models.CharField(max_length=100)
	order_no=models.AutoField(primary_key=True)
	name = models.CharField(max_length = 100,null=True,blank =True)
	phone = models.CharField(max_length = 12)
	email = models.EmailField(max_length = 75,null=True,blank =True)
	#address=models.CharField(max_length = 300)
	#flat_no=models.CharField(max_length = 100,null=True,blank =True)
	address1=models.CharField(max_length = 300,null=True,blank =True)
	address2=models.CharField(max_length = 300,null=True,blank =True)
	city=models.CharField(max_length = 50,null=True,blank =True)
	state=models.CharField(max_length = 50,null=True,blank =True)
	pincode=models.CharField(max_length =30,null=True,blank =True)
	country=models.CharField(max_length =30,null=True,blank =True)
	payment_method=models.CharField(max_length=1,choices=(('F','free checkout') ,('C','cod'),),)
	book_time=models.DateTimeField(null=True,blank=True)
	status=models.CharField(max_length=1,choices=(('P','pending') ,('C','complete'),('N','cancelled'),('D','delivered'),),default='P')
	method=models.CharField(max_length=1,
									  choices=(('B','Bulk') ,('N','Normal'),),
									  blank=True , null = True)

	business=models.ForeignKey(Business)
	'''

admin.site.register(Order, OrderAdmin)

'''
class ShipmentAdmin(admin.ModelAdmin):
	list_per_page = 10
	form=ShipmentForm


	search_fields=['order__order_no','real_tracking_no','mapped_tracking_no','drop_phone','drop_name']
	list_display = ('real_tracking_no','name','cost_of_courier','weight','mapped_tracking_no','company','parcel_details','price','category','drop_phone','drop_name','status','address','print_invoice','generate_order')
	list_filter=['category']
	list_editable = ('name','cost_of_courier','weight','mapped_tracking_no','company','price','category','drop_phone','drop_name',)
	readonly_fields=('real_tracking_no','print_invoice','generate_order','parcel_details','address')

	fieldsets=(
		('Basic Information', {'fields':['real_tracking_no','parcel_details',('category','status')],'classes':('suit-tab','suit-tab-general')}),
		('Parcel Information', {'fields':[('name','weight','cost_of_courier'),],'classes':('suit-tab','suit-tab-general')}),
		('Amount paid', {'fields':['price',],'classes':('suit-tab','suit-tab-general')}),
		('Tracking Information', {'fields':[('mapped_tracking_no','company'),],'classes':('suit-tab','suit-tab-general')}),
		#('Destination Address', {'fields':['drop_name','drop_phone','drop_flat_no','locality','city','state','drop_pincode','country'] , 'classes':['collapse',]})
		('Destination Address', {'fields':[('drop_name','drop_phone'),'address',] ,'classes':('suit-tab','suit-tab-general')}),
		('Actions',{'fields':['print_invoice','generate_order'],'classes':('suit-tab','suit-tab-general')}),
		('Tracking',{'fields':['tracking_data'],'classes':('suit-tab','suit-tab-tracking')})
		)

	suit_form_tabs = (('general', 'General'), ('tracking', 'Tracking'))

'''
from daterange_filter.filter import DateRangeFilter

class RemittanceProductPendingAdmin(admin.ModelAdmin):
    list_filter=['order__business',('date', DateRangeFilter),]
    list_editable=['remittance',]
    list_display = (
        'get_order_no','order_link', 'date', 'get_business', 'name', 'cod_cost', 'shipping_cost', 'status',
        'price','remittance')
    readonly_fields = (
        'name', 'quantity', 'sku', 'price', 'weight', 'applied_weight', 'real_tracking_no', 'order', 'tracking_data',
        'kartrocket_order', 'shipping_cost', 'cod_cost', 'date','barcode',)

    def get_order_no(self, obj):
        return obj.order.order_no
    get_order_no.admin_order_field  = 'order_no'  #Allows column order sorting
    get_order_no.short_description = 'Order No'

    def order_link(self, obj):
        return '<a href="/admin/businessapp/order/%s/">%s</a>' % (obj.order.pk, obj.order.pk)
    order_link.allow_tags = True

    def get_business(self, obj):
        return obj.order.business
    get_business.admin_order_field  = 'business'  #Allows column order sorting
    get_business.short_description = 'Business'

    def queryset(self, request):
        return self.model.objects.filter(order__payment_method='C').order_by('status').exclude(remittance=True)



admin.site.register(RemittanceProductPending, RemittanceProductPendingAdmin)

class RemittanceProductCompleteAdmin(admin.ModelAdmin):
    list_filter=['order__business',('date', DateRangeFilter),]
    list_editable=['remittance',]
    list_display = (
        'get_order_no', 'order_link','date', 'get_business', 'name', 'cod_cost', 'shipping_cost', 'status',
        'price','remittance')
    readonly_fields = (
        'name', 'quantity', 'sku', 'price', 'weight', 'applied_weight', 'real_tracking_no', 'order', 'tracking_data',
        'kartrocket_order', 'shipping_cost', 'cod_cost', 'date','barcode',)

    def get_order_no(self, obj):
        return obj.order.order_no
    get_order_no.admin_order_field  = 'order_no'  #Allows column order sorting
    get_order_no.short_description = 'Order No'

    def order_link(self, obj):
        return '<a href="/admin/businessapp/order/%s/">%s</a>' % (obj.order.pk, obj.order.pk)
    order_link.allow_tags = True

    def get_business(self, obj):
        return obj.order.business
    get_business.admin_order_field  = 'business'  #Allows column order sorting
    get_business.short_description = 'Business'

    def queryset(self, request):
        return self.model.objects.filter(order__payment_method='C').order_by('status').exclude(remittance=False)



admin.site.register(RemittanceProductComplete, RemittanceProductCompleteAdmin)


class QcProductAdmin(ProductAdmin):
    def queryset(self, request):
        return self.model.objects.filter(order__status='DI')
    list_display = (
        'real_tracking_no', 'tracking_status' ,'update_time','barcode','get_method','get_business')
    list_filter = ['order__method','order__business']
    list_editable = ()
# readonly_fields = ('order__method','drop_phone', 'drop_name', 'status', 'address','barcode','tracking_data','real_tracking_no','name','weight','cost_of_courier','price')
    search_fields = ['order__order_no', 'real_tracking_no', 'mapped_tracking_no', 'drop_phone', 'drop_name']
    def get_method(self, obj):
        if (obj.order.method=='B'):
            return 'Bulk'
        elif (obj.order.method=='N'):
            return 'Normal'
        else:
            return 'None'
    get_method.admin_order_field = 'order__method' #Allows column order sorting
    get_method.short_description = 'method'
    def tracking_status(self, obj):
#pk=obj.namemail.pk
        return json.loads(obj.tracking_data)[-1]['status']
    tracking_status.allow_tags = True
    tracking_status.admin_order_field = 'tracking_data'

    def get_business(self, obj):
        return obj.order.business
    get_business.short_description = 'business'
    get_business.admin_order_field = 'order__business'


admin.site.register(QcProduct, QcProductAdmin)