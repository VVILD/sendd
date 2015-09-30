import urllib
import json
from django.contrib.admin import ModelAdmin, RelatedFieldListFilter

from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from random import randint

from datetime import timedelta
import datetime
from datetime import date
from django.contrib import admin
from .models import *
import reversion

from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch
from django.db.models import Sum
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.utils.html import escape
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.auth.models import User

from django.utils import timezone


action_names = {
    ADDITION: 'Addition',
    CHANGE:   'Change',
    DELETION: 'Deletion',
}

class FilterBase(admin.SimpleListFilter):
    def queryset(self, request, queryset):
        if self.value():
            dictionary = dict(((self.parameter_name, self.value()),))
            return queryset.filter(**dictionary)

class ActionFilter(FilterBase):
    title = 'action'
    parameter_name = 'action_flag'
    def lookups(self, request, model_admin):
        return action_names.items()


class UserFilter(FilterBase):
    """Use this filter to only show current users, who appear in the log."""
    title = 'user'
    parameter_name = 'user_id'
    def lookups(self, request, model_admin):
        return tuple((u.id, u.username)
            for u in User.objects.filter(pk__in =
                LogEntry.objects.values_list('user_id').distinct())
        )

class AdminFilter(UserFilter):
    """Use this filter to only show current Superusers."""
    title = 'admin'
    def lookups(self, request, model_admin):
        return tuple((u.id, u.username) for u in User.objects.filter(is_superuser=True))

class StaffFilter(UserFilter):
    """Use this filter to only show current Staff members."""
    title = 'staff'
    def lookups(self, request, model_admin):
        return tuple((u.id, u.username) for u in User.objects.filter(is_staff=True))


class LogEntryAdmin(admin.ModelAdmin):

    date_hierarchy = 'action_time'

    readonly_fields = ('user','content_type','object_repr','object_id','change_message')

    list_filter = [
        UserFilter,
        ActionFilter,
        'content_type',
        # 'user',
    ]

    search_fields = [
        'object_repr',
        'change_message'
    ]


    list_display = [
        'action_time',
        'user',
        'content_type',
        'object_link',
        'action_flag',
        'action_description',
        'change_message',
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser and request.method != 'POST'

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        ct = obj.content_type
        repr_ = escape(obj.object_repr)
        try:
            href = reverse('admin:%s_%s_change' % (ct.app_label, ct.model), args=[obj.object_id])
            link = u'<a href="%s">%s</a>' % (href, repr_)
        except NoReverseMatch:
            link = repr_
        return link if obj.action_flag != DELETION else repr_
    object_link.allow_tags = True
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = u'object'

    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')

    def action_description(self, obj):
        return action_names[obj.action_flag]
    action_description.short_description = 'Action'


admin.site.register(LogEntry, LogEntryAdmin)


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

# <a class="btn btn-info" href="/admin/businessapp/business/notapprovedbusiness/"><span class="badge">{{nap}}</span> Not Approved</a>
# <a class="btn btn-info" href="/admin/businessapp/business/approvedbusiness/"><span class="badge">{{ap}}</span>Approved</a>
# <a class="btn btn-info" href="/admin/businessapp/business/cancelledbusiness/"><span class="badge">{{c}}</span>cancelled</a>
# <a class="btn btn-info" href="/admin/businessapp/business/dailybusiness/"><span class="badge">{{d}}</span>daily</a>
# </center>
# <br>
# <br>



# <!-- <div class="col-md-6">Today Customers Orders
# <br>
# <li># orders: {{count_b2c}}</li>
# <li>Total revenue: {{sum_b2c}}</li>
# </div> -->
# {% elif op %}
# <center>
# <div class="row">
# <a class="btn btn-info" href="/admin/businessapp/business/approvedbusinessop/"><span class="badge">{{ap}}</span> Approved business</a>
# <a class="btn btn-info" href="/admin/businessapp/order/?q=&status__exact=P"><span class="badge">{{p}}</span>Pending orders </a>
# <a class="btn btn-info" href="/admin/businessapp/order/?q=&status__exact=PU"><span class="badge">{{pu}}</span>Picked up orders</a>
# <a class="btn btn-info" href="/admin/businessapp/order/?q=&status__exact=DI"><span class="badge">{{di}}</span>Dispatched orders</a>
# <br>
# <br>
class BaseBusinessAdmin(reversion.VersionAdmin):

    

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
        a = Business.objects.filter(status='A',is_completed=False).count()
        
        nap = Order.objects.filter(business__status='N',status='P').count()
        ap = Business.objects.filter(status='Y').count()
        apcs=Business.objects.filter().exclude(status='N').count()
        d = Business.objects.filter(daily=True).count()
        c = Business.objects.filter(status='C').count()
        #pa = Business.objects.filter(order_status='AP').count()
        #c = Business.objects.filter(order_status='DI').count()
        p= Order.objects.filter(status='P').count()
        pu= Order.objects.filter(status='PU').count()
        di= Order.objects.filter(status='DI').count()
        un= Order.objects.filter(status__in=['PU','D']).count()
        picked= Business.objects.filter(is_completed=True,status='A').count()

        context = {'cs':cs,'op':op,'nap':nap,'ap':ap,'d':d,'c':c,'p':p,'pu':pu,'di':di,'a':a,'apcs':apcs,'un':un,'picked':picked}
        return super(BaseBusinessAdmin, self).changelist_view(request, extra_context=context)


# Register your models here.
class BusinessAdmin(BaseBusinessAdmin):
    # search_fields=['name']
    search_fields=['username','business_name']
    list_display = ('username','business_name', 'pickup_time', 'warehouse', 'pb', 'assigned_pickup_time','status', 'pending_orders_total', 'pending_orders','pickedup_orders','dispatched_orders','daily','cs_comment','ff_comment')
    list_editable = ('pb', 'assigned_pickup_time','daily','cs_comment','ff_comment')
    raw_id_fields = ('pb', 'warehouse')
    list_filter = ['username', 'daily','pb', 'warehouse']

    #actions = [export_as_csv_action("CSV Export", fields=['username','business_name','apikey','name','email','contact_mob','contact_office','address','city','state','pincode'])]
    actions_on_bottom = False
    actions_on_top = True
    

    def get_queryset(self, request):
#total_order
#pick_order
#pending_count
#transit_count
#dispatch_count
        todays_date=date.today()
        import datetime
        date_max = datetime.datetime.combine(todays_date, datetime.time.max)
        date_min = datetime.datetime.combine(todays_date, datetime.time.min)
        


        return Business.objects.extra(select={
            'pending': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='P' ",
            'picked': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='PU' ",
            'transit': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='D' ",
            'dispatch': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='DI' ",
            'pending_today': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='P' and businessapp_order.book_time BETWEEN %s AND %s",
            'pickedup_today': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='PU' and businessapp_order.book_time BETWEEN %s AND %s",
            'dispatched_today': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='DI' and businessapp_order.book_time BETWEEN %s AND %s",},
            select_params=(date_min,date_max,date_min,date_max,date_min,date_max,),
            )


# Business.objects.extra(select={'pending': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='P' ",'picked': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='PU' ",'transit': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='D' ",'dispatch': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='DI' ",'pending_today': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='P' and businessapp_order.book_time BETWEEN '2015-09-07 00:00:00' AND '2015-09-07 23:59:59'",},)


    def pricing_ok(self,obj):
        try:
            Pricing.objects.get(business=obj.username)
            return True
        except:
            return False
    pricing_ok.boolean = True


    def pending_orders_total(self, obj):

        return '<a href="/admin/businessapp/order/?q=&business__username__exact=%s&status__exact=P"> %s </a>' % (
            obj.username, obj.pending)

    pending_orders_total.allow_tags = True
    pending_orders_total.admin_order_field='pending'

    def pickedup_orders(self, obj):
        return '<a href="/admin/businessapp/order/?q=&business__username__exact=%s&status__exact=PU"> %s </a>' % (obj.username, obj.pickedup_today)
    pickedup_orders.allow_tags = True
    pickedup_orders.admin_order_field='pickedup_today'

    def dispatched_orders(self, obj):
        return '<a href="/admin/businessapp/order/?q=&business__username__exact=%s&status__exact=DI"> %s </a>' % (obj.username, obj.dispatched_today)
    dispatched_orders.allow_tags = True
    dispatched_orders.admin_order_field='dispatched_today'


    def pending_orders(self, obj):
        return '<a href="/admin/businessapp/order/?q=&business__username__exact=%s&status__exact=P"> %s </a>' % (obj.username, obj.pending_today)
    pending_orders.allow_tags = True
    pending_orders.admin_order_field = 'pending_today'


class CSBusinessAdmin(BusinessAdmin):
    # search_fields=['name']
    search_fields=['username','business_name']
    list_display = ( 'business_name','contact_mob','contact_office', 'pickup_time','pb','assigned_pickup_time','status','pending_orders_total', 'pending_orders','pickedup_orders','dispatched_orders','daily','cs_comment','warehouse','pricing_ok')
    list_editable = ('assigned_pickup_time','cs_comment')
    list_filter = ['username', 'daily','pb']

    def get_queryset(self, request):
#total_order
#pick_order
#pending_count
#transit_count
#dispatch_count
        todays_date=date.today()
        import datetime
        date_max = datetime.datetime.combine(todays_date, datetime.time.max)
        date_min = datetime.datetime.combine(todays_date, datetime.time.min)
        


        return Business.objects.extra(select={
            'pending': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='P' ",
            'picked': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='PU' ",
            'transit': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='D' ",
            'dispatch': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='DI' ",
            'pending_today': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='P' and businessapp_order.book_time BETWEEN %s AND %s",
            'pickedup_today': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='PU' and businessapp_order.book_time BETWEEN %s AND %s",
            'dispatched_today': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='DI' and businessapp_order.book_time BETWEEN %s AND %s",},
            select_params=(date_min,date_max,date_min,date_max,date_min,date_max,),
            )


class OPBusinessAdmin(BusinessAdmin):
    # search_fields=['name']
    search_fields=['username','business_name']
    list_display = ( 'business_name', 'warehouse', 'pickup_time', 'pb', 'assigned_pickup_time','status','pending_orders_total', 'pending_orders','pickedup_orders','dispatched_orders','cs_comment','ff_comment')
    list_editable = ('pb', 'warehouse','ff_comment')
    raw_id_fields = ('pb', 'warehouse')
    list_filter = ['username', 'daily','pb', 'warehouse']


class NotApprovedBusinessAdmin(CSBusinessAdmin):
    def make_approved(modeladmin, request, queryset):
        ct = ContentType.objects.get_for_model(queryset.model)
        for obj in queryset:
            LogEntry.objects.log_action(
                user_id=request.user.id, 
                content_type_id=ct.pk,
                object_id=obj.pk,
                object_repr=str(obj.pk),
                action_flag=CHANGE,
                change_message="action button : business status changed to approved")        
        queryset.update(status='Y',pb=None,is_completed=False)



    make_approved.short_description = "approve"


    actions = [make_approved]
    actions_on_bottom = False
    actions_on_top = True


    def get_queryset(self, request):
        qs = super(CSBusinessAdmin, self).queryset(request)
        qs = qs.filter(status='N')
        return qs


    # def get_queryset(self, request):

    #     return Business.objects.raw('SELECT `businessapp_business`.`username`, `businessapp_business`.`apikey`, `businessapp_business`.`business_name`, `businessapp_business`.`password`, `businessapp_business`.`email`, `businessapp_business`.`name`, `businessapp_business`.`contact_mob`, `businessapp_business`.`contact_office`, `businessapp_business`.`pickup_time`, `businessapp_business`.`address`, `businessapp_business`.`city`, `businessapp_business`.`state`, `businessapp_business`.`pincode`, `businessapp_business`.`company_name`, `businessapp_business`.`website`, `businessapp_business`.`businessmanager_id`, `businessapp_business`.`show_tracking_company`, `businessapp_business`.`pb_id`, `businessapp_business`.`assigned_pickup_time`, `businessapp_business`.`comment`, `businessapp_business`.`daily`, `businessapp_business`.`status`, `businessapp_business`.`warehouse_id`, COUNT(`businessapp_order`.`status`) AS `total_order` ,count(case when `businessapp_order`.`status` = 'PU' then 1 end) as pick_order,count(case when `businessapp_order`.`status` = 'P' then 1 end) as pending_count, count(case when `businessapp_order`.`status` = 'D' then 1 end) as transit_count,count(case when `businessapp_order`.`status` = 'DI' then 1 end) as dispatch_count  FROM `businessapp_business` INNER JOIN `businessapp_order` ON ( `businessapp_business`.`username` = `businessapp_order`.`business_id` ) GROUP BY `businessapp_business`.`username` ORDER BY NULL')


admin.site.register(NotApprovedBusiness, NotApprovedBusinessAdmin)


class ApprovedBusinessAdmin(CSBusinessAdmin):
    


    def make_not_approved(modeladmin, request, queryset):
        ct = ContentType.objects.get_for_model(queryset.model)
        for obj in queryset:
            LogEntry.objects.log_action(
                user_id=request.user.id, 
                content_type_id=ct.pk,
                object_id=obj.pk,
                object_repr=str(obj.pk),
                action_flag=CHANGE,
                change_message="action button : business status changed to not approved")
        queryset.update(status='N')

    make_not_approved.short_description = "make not approve"


    actions = [make_not_approved]

    actions_on_bottom = False
    actions_on_top = True


    def get_queryset(self, request):
        qs = super(CSBusinessAdmin, self).queryset(request)
        qs = qs.exclude(status='N')
        return qs


admin.site.register(ApprovedBusiness, ApprovedBusinessAdmin)

class DailyBusinessAdmin(CSBusinessAdmin):
    
    def get_queryset(self, request):
        return self.model.objects.filter(daily='True')


admin.site.register(DailyBusiness, DailyBusinessAdmin)

class CancelledBusinessAdmin(CSBusinessAdmin):
    
    def get_queryset(self, request):
        return self.model.objects.filter(status='C')


admin.site.register(CancelledBusiness, CancelledBusinessAdmin)

class ApprovedBusinessOPAdmin(OPBusinessAdmin):
    
    def make_alloted(modeladmin, request, queryset):
        ct = ContentType.objects.get_for_model(queryset.model)
        for obj in queryset:
            LogEntry.objects.log_action(
                user_id=request.user.id, 
                content_type_id=ct.pk,
                object_id=obj.pk,
                object_repr=str(obj.pk),
                action_flag=CHANGE,
                change_message="action button : business status changed to alloted")
        queryset.update(status='A')



    make_alloted.short_description = "make alloted"


    actions = [make_alloted]

    actions_on_bottom = False
    actions_on_top = True


    
    def get_queryset(self, request):
        qs = super(OPBusinessAdmin, self).queryset(request)
        qs = qs.filter(status='Y',is_completed=False)
        return qs


admin.site.register(ApprovedBusinessOP, ApprovedBusinessOPAdmin)


class AllotedBusinessAdmin(OPBusinessAdmin):

    def make_pickedup(modeladmin, request, queryset):
        ct = ContentType.objects.get_for_model(queryset.model)
        for obj in queryset:
            LogEntry.objects.log_action(
                user_id=request.user.id, 
                content_type_id=ct.pk,
                object_id=obj.pk,
                object_repr=str(obj.pk),
                action_flag=CHANGE,
                change_message="action button : business status changed to picked up")
        queryset.update(is_completed=True)



    make_pickedup.short_description = "make pickedup"

    actions_on_bottom = False
    actions_on_top = True

    actions = [make_pickedup]
    
    def get_queryset(self, request):
        qs = super(OPBusinessAdmin, self).queryset(request)
        qs = qs.filter(status='A',is_completed=False)
        return qs


admin.site.register(AllotedBusiness, AllotedBusinessAdmin)


class PickedupBusinessAdmin(OPBusinessAdmin):

    def make_complete(modeladmin, request, queryset):
        ct = ContentType.objects.get_for_model(queryset.model)
        for obj in queryset:
            LogEntry.objects.log_action(
                user_id=request.user.id, 
                content_type_id=ct.pk,
                object_id=obj.pk,
                object_repr=str(obj.pk),
                action_flag=CHANGE,
                change_message="action button : business status changed to complete")
        queryset.update(status='N',pb=None,is_completed=False)



    make_complete.short_description = "make complete"

    actions_on_bottom = False
    actions_on_top = True

    actions = [make_complete]
    
    def get_queryset(self, request):
        qs = super(OPBusinessAdmin, self).queryset(request)
        qs = qs.filter(is_completed=True,status='A')
        print qs
        return qs


admin.site.register(PickedupBusiness, PickedupBusinessAdmin)




from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

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


class ProductAdmin(reversion.VersionAdmin):
    search_fields = ['name', 'real_tracking_no']
    list_display = ('name', 'price', 'weight', 'status', 'real_tracking_no', 'order', 'barcode','date','last_tracking_status','update_time')
    list_editable = ('status', )
    list_filter=['order__business','last_tracking_status','company','status']
    readonly_fields = (
        'name', 'quantity', 'sku', 'price', 'weight', 'applied_weight', 'real_tracking_no', 'order',
        'kartrocket_order', 'shipping_cost', 'cod_cost', 'status', 'date', 'barcode')


    fieldsets = (
        ('Tracking_details', {'fields': ['mapped_tracking_no', 'company','real_tracking_no','kartrocket_order'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('General', {'fields': ['name', 'quantity','sku','price','weight','applied_weight','status','date','remittance','order'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Cost', {'fields': ['shipping_cost', 'cod_cost','return_cost'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Tracking', {'fields': ['tracking_data'], 'classes': ('suit-tab', 'suit-tab-tracking')}),
        ('Barcode', {'fields': ['barcode','tracking_history'], 'classes': ('suit-tab', 'suit-tab-barcode')}),
    )

    suit_form_tabs = (('general', 'General'), ('tracking', 'Tracking'),('barcode', 'Barcode'))

    actions = [export_as_csv_action("CSV Export", fields=['name','real_tracking_no','order__name'])]

admin.site.register(Product, ProductAdmin)

admin.site.register(Payment)
admin.site.register(Forgotpass)

class PricingAdmin(reversion.VersionAdmin):
    # search_fields=['name']
    list_filter=('business__username','business__business_name')


admin.site.register(Pricing,PricingAdmin)



class BarcodeAdmin(reversion.VersionAdmin):
    # search_fields=['name']
    list_filter=('business',)
    list_display=('value','created_at','business')


admin.site.register(Barcode,BarcodeAdmin)


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
        'product_info', 'name', 'quantity', 'price', 'weight', 'applied_weight', 'is_document', 'generate_order', 'fedex')
    extra = 0

    def product_info(self, obj):
        return '<b>Name:</b>' + str(obj.name) + '<br>' + '<b>Quantity:</b>' + str(
            obj.quantity) + '<br>' + 'SKU: ' + str(obj.sku) + '<br>' + '<b>Price:</b>' + str(
            obj.price) + '<br>' + "<b>tracking_no:</b>" + str(
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
        cod=''
        valid = 1
        try:
            string = 'ot=1&'
            product = Product.objects.get(pk=obj.pk)
            order = product.order
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
                error_string = error_string + 'item_name not set<br>'
                valid = 0

            try:
                price = product.price

                if (str(price) != '' and str(price) != 'None'):
                    string = string + 'price=' + str(price) + '&'
                else:
                    error_string = error_string + 'item_cost not set<br>'
                    valid = 0
            except:
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
                error_string = error_string + 'drop_phone not set<br>'
                valid = 0

            try:
                address1 = str(order.address1)
                string = string + 'address=' + str(address1) + '&'
            except:
                error_string = error_string + 'address 1 not set<br>'
                valid = 0

            try:
                address2 = str(order.address2)
                string = string + 'address1=' + str(address2) + '&'
            except:
                error_string = error_string + 'address 2 not set<br>'
                valid = 0

            try:
                city = order.city
                string = string + 'city=' + str(city) + '&'
            except:
                error_string = error_string + 'city not set<br>'
                valid = 0

            try:
                state = order.state
                string = string + 'state=' + str(state) + '&'
            except:
                error_string = error_string + 'state not set<br>'
                valid = 0

            try:
                pincode = order.pincode
                string = string + 'pincode=' + str(pincode) + '&'
            except:
                error_string = error_string + 'pincode not set<br>'
                valid = 0

            try:

                cod = order.payment_method
                string = string + 'cod=' + str(cod) + '&'
            except:
                error_string = error_string + 'cod not set<br>'
                valid = 0

        except:
            pass

        if (valid):
            if (cod=='F'):
                return 'All good!<br><a href="/stats/kartrocket/?%s" target="_blank" >Create Normal Order</a>' % (string)
            elif (cod=='C'):
                return 'All good!<br><a href="/stats/kartrocket/?%s" target="_blank" >Create Cod Order</a>' % (string)
            else:
                return "no payment_method set"
        else:
            return '<div style="color:red">' + error_string + '</div>'

    generate_order.allow_tags = True

    def fedex(self, obj):
        params = urllib.urlencode({'shipment_pk': obj.pk, 'client_type': "business"})

        if not obj.order.state:
            return "Enter state"

        if not state_matcher.is_state(obj.order.state):
            return '<h2 style="color:red">Enter a valid state</h2>'

        if not obj.order.pincode:
            return "Enter pincode"

        db_pincode = Pincode.objects.filter(pincode=obj.order.pincode)

        if db_pincode:
            if not db_pincode[0].fedex_servicable:
                return '<h2 style="color:red">Not Servicable</h2>'
            elif db_pincode[0].fedex_oda_opa:
                return '<h2 style="color:red">ODA</h2>'
        else:
            return '<h2 style="color:red">Enter a valid pincode</h2>'

        if obj.order.payment_method == 'C':
            if not db_pincode[0].fedex_cod_service:
                return '<h2 style="color:red">Not COD Servicable</h2>'

        if not obj.applied_weight:
            return "Enter applied weight"

        if not obj.price:
            return "Enter item value"

        if obj.order.state == 'Kerala' and obj.order.method == 'B':
            return '<h2 style="color:red">Not Servicable</h2>'

        # Temporary ban
        if obj.order.state == 'Kerala' and obj.order.payment_method == 'C':
            return '<h2 style="color:red">Kerala Temporary Ban</h2>'

        if obj.order.state == 'West Bengal' and float(obj.price) > 1000:
            return '<h2 style="color:red">Not Servicable</h2>'

        if obj.fedex_ship_docs:
            if obj.order.state == 'Gujarat' and obj.order.method == 'B':
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_ship_docs.name).split('/')[-1], "Print Docs")+'<br><br>' + '<br><br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order") + '<br><br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
            else:
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_ship_docs.name).split('/')[-1], "Print Docs")+'<br><br>' + '<br><br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order")

        if obj.fedex_outbound_label and obj.fedex_cod_return_label:
            if obj.order.state == 'Gujarat' and obj.order.method == 'B':
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label")+'<br><br>'+ '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_cod_return_label.name).split('/')[-1], "Print COD Return Label") + '<br><br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order") + '<br><br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
            else:
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label")+'<br><br>'+ '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_cod_return_label.name).split('/')[-1], "Print COD Return Label") + '<br><br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order")
        elif obj.fedex_outbound_label:
            if obj.order.state == 'Gujarat' and obj.order.method == 'B':
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label") + '<br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order") + '<br><br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
            else:
                return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label") + '<br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order")

        if obj.order.state == 'Gujarat' and obj.order.method == 'B':
            return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<br> <br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"

        if state_matcher.is_restricted(obj.order.state) and not obj.is_document:
            return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<br> <h2 style="color:red">Restricted States</h2>'

        return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order")

    fedex.allow_tags = True


# fieldsets=(
# ('Basic Information', {'fields':['real_tracking_no','print_invoice',], 'classes':('suit-tab','suit-tab-general')}),
# 	#('Address', {'fields':['flat_no','address','pincode',], 'classes':('suit-tab','suit-tab-general')}),
# 	#('Destination Address', {'fields':['drop_name','drop_phone','drop_flat_no','locality','city','state','drop_pincode','country'] , 'classes':['collapse',]})
# 	#('Invoices',{'fields':['send_invoice',], 'classes':('suit-tab','suit-tab-invoices')})
# )
# suit_form_tabs = (('general', 'General'))
class FilterUserAdmin(BaseBusinessAdmin):


    def get_queryset(self, request):
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
    search_fields = ['order_no','business__business_name', 'name', 'product__real_tracking_no', 'product__barcode','city','state','product__mapped_tracking_no']
    list_display = (
        'order_no', 'book_time', 'business_details', 'name', 'status','mapped_ok', 'no_of_products', 'total_shipping_cost',
        'total_cod_cost', 'method',)
    list_editable = ('status',)
    list_filter = ['business', 'status', 'book_time']
    actions = [export_as_csv_action("CSV Export", fields=['name','product__real_tracking_no'])]
    readonly_fields=('master_tracking_number',)


    def change_view(self, request, object_id, form_url='', extra_context=None):        
        extra_context = extra_context or {}
        extra_context['x'] = object_id
        return super(OrderAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

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
            return {'class': css_class, 'data': obj.name}

    def business_details(self, obj):
        return '<a href="/admin/businessapp/business/%s/">%s</a>' % (obj.business.username, obj.business.business_name)

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
class ShipmentAdmin(reversion.VersionAdmin):
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

class RemittanceProductPendingAdmin(reversion.VersionAdmin):
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

    def get_queryset(self, request):
        return self.model.objects.filter(order__payment_method='C').order_by('status').exclude(remittance=True)



admin.site.register(RemittanceProductPending, RemittanceProductPendingAdmin)

class RemittanceProductCompleteAdmin(reversion.VersionAdmin):
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

    def get_queryset(self, request):
        return self.model.objects.filter(order__payment_method='C').order_by('status').exclude(remittance=False)



admin.site.register(RemittanceProductComplete, RemittanceProductCompleteAdmin)


reversion.VersionAdmin.change_list_template='businessapp/templates/admin/businessapp/change_list.html'

class QcProductAdmin(ProductAdmin):

    change_list_template='businessapp/templates/admin/businessapp/qcproduct/change_list.html'
    def get_queryset(self, request):
        return self.model.objects.filter(Q(order__status='DI')| Q(order__status='R')).exclude(status='C').exclude(order__business='ecell').exclude(order__business='ghasitaram').exclude(order__business='holachef')
    list_display = (
        'order_no','tracking_no','company','book_date','dispatch_time','get_business','sent_to', 'tracking_status','last_location' ,'expected_delivery_date','last_updated','last_tracking_status','qc_comment')
    list_filter = ['order__method','order__business','last_tracking_status','warning','company']
    list_editable = ('qc_comment',)
# readonly_fields = ('order__method','drop_phone', 'drop_name', 'status', 'address','barcode','tracking_data','real_tracking_no','name','weight','cost_of_courier','price')
    search_fields = ['order__order_no', 'real_tracking_no', 'mapped_tracking_no','tracking_data' ]
    
    fieldsets = (
        ('Tracking_details', {'fields': ['mapped_tracking_no', 'company','real_tracking_no','kartrocket_order','qc_comment'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('General', {'fields': ['name', 'quantity','sku','price','weight','applied_weight','status','date','remittance','order'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Cost', {'fields': ['shipping_cost', 'cod_cost','return_cost'], 'classes': ('suit-tab', 'suit-tab-general')}),
        ('Tracking', {'fields': ['tracking_data'], 'classes': ('suit-tab', 'suit-tab-tracking')}),
        ('Barcode', {'fields': ['barcode','tracking_history'], 'classes': ('suit-tab', 'suit-tab-barcode')}),
    )


    def order_no(self, obj):
        return '<a href="/admin/businessapp/order/%s/">%s</a>' % (obj.order.pk, obj.order.pk)
    order_no.allow_tags = True
    order_no.admin_order_field = 'order'


    def get_method(self, obj):
        if (obj.order.method=='B'):
            return 'Bulk'
        elif (obj.order.method=='N'):
            return 'Normal'
        else:
            return 'None'
    get_method.admin_order_field = 'order__method' #Allows column order sorting
    get_method.short_description = 'method'

    def tracking_no(self, obj):
        if (obj.company=='B'):
            return '<a href="http://www.bluedart.com/servlet/RoutingServlet?handler=tnt&action=awbquery&awb=awb&numbers=%s" target="_blank">%s</a>' % (obj.mapped_tracking_no, obj.mapped_tracking_no)
        elif (obj.company=='F'):
            return '<a href="https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber=%s" target="_blank" >%s</a> ' % (obj.mapped_tracking_no, obj.mapped_tracking_no)
        else:
            return obj.mapped_tracking_no
    tracking_no.admin_order_field = 'mapped_tracking_no' #Allows column order sorting
    tracking_no.allow_tags=True
    
    def expected_delivery_date(self,obj):
        if (obj.order.method=='B'):
            return obj.date + timedelta(days=6)
        elif (obj.order.method=='N'):
            return obj.date + timedelta(days=3)
        else:
            return 'None'
    expected_delivery_date.short_description='expected delivery date'

    def tracking_status(self, obj):
#pk=obj.namemail.pk
        return json.loads(obj.tracking_data)[-1]['status']
    tracking_status.allow_tags = True
    tracking_status.admin_order_field = 'tracking_data'

    def sent_to(self,obj):
        return obj.order.name

    def book_date(self,obj):
        return obj.date
    book_date.admin_order_field='date'

    def last_updated(self,obj):
        import datetime
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = timezone.now()
        #time = ind_time.strftime(fmt)
        #fmt = '%Y-%m-%d %H:%M:%S'
        try:
            diff_time=ind_time-obj.update_time
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

    def last_location(self, obj):
#pk=obj.namemail.pk
        return json.loads(obj.tracking_data)[-1]['location']
    last_location.allow_tags = True
    last_location.admin_order_field = 'tracking_data'

    def get_business(self, obj):
        return obj.order.business
    get_business.short_description = 'business'
    get_business.admin_order_field = 'order__business'

    def suit_row_attributes(self, obj, request):
        css_class = {False: 'success',True: 'error',}.get(obj.warning)
        if css_class:
            return {'class': css_class, 'data': obj.name}


admin.site.register(QcProduct, QcProductAdmin)


class Pricing2Admin(reversion.VersionAdmin):
    # search_fields=['name']
    list_filter=('business__username','business__business_name','zone','weight','type')
    list_display=('business','weight','zone','type','price','ppkg')
    list_editable = ('price',)

admin.site.register(Pricing2,Pricing2Admin)


class WeightAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Weight,WeightAdmin)

class ZoneAdmin(reversion.VersionAdmin):
    pass

admin.site.register(Zone,ZoneAdmin)

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class BmFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Businessmanager')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'decade'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        bd_set=Profile.objects.filter(usertype='b')
        bd_tupel=[]

        bd_tupel.append(('nbm',_('No businessmanager')))
        for bd in bd_set:
            bd_tupel.append((bd.user.username,_(bd.user.username)))


        print (bd_tupel,)
        return tuple(bd_tupel)
        # return (
        #     ('80s', _('in the eighties')),
        #     ('90s', _('in the nineties')),
        # )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        # if self.value() == '80s':
        #     return queryset.filter(birthday__gte=date(1980, 1, 1),
        #                             birthday__lte=date(1989, 12, 31))
        # if self.value() == '90s':
        #     return queryset.filter(birthday__gte=date(1990, 1, 1),
        #                             birthday__lte=date(1999, 12, 31))

        if self.value()==None:
            return queryset.filter()
        if self.value()=='nbm':
            return queryset.filter(businessmanager__isnull=True)


        return queryset.filter(businessmanager__user__username=self.value())

class BdheadAdmin(admin.ModelAdmin):
    # search_fields=['name']

    def get_queryset(self, request):
        todays_date=date.today()
        import datetime
        date_max = datetime.datetime.combine(todays_date, datetime.time.max)
        date_min = datetime.datetime.combine(todays_date, datetime.time.min)

#'order_total','order_today','total_completed','total_revenue',

        return Business.objects.extra(select={
            'order_total2': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username ",
            'total_completed2': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='C' ",
            'order_today2': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.book_time BETWEEN %s AND %s",},
            select_params=(date_min,date_max,date_min,date_max,date_min,date_max,),
            )
    search_fields=['username','business_name']
    list_display = ('username','business_name', 'warehouse', 'businessmanager','order_total','order_today','total_completed','total_revenue')
    #aw_id_fields = ('pb', 'warehouse')
    list_filter = ['warehouse',BmFilter,]


    actions = [export_as_csv_action("CSV Export", fields=['username','business_name','apikey','name','email','contact_mob','contact_office','address','city','state','pincode'])]
    actions_on_bottom = False
    actions_on_top = True



    def total_revenue(self,obj):
        today_orders_b2b = Order.objects.filter(business=obj.username)
        today_products_correct = Product.objects.filter(order=today_orders_b2b).exclude(shipping_cost__isnull=True)
        sum_b2b = today_products_correct.aggregate(total=Sum('shipping_cost', field="shipping_cost+cod_cost"))['total']
        count_b2b = today_products_correct.count()

        print sum_b2b
        print count_b2b
        return sum_b2b

    def order_total(self,obj):
                return '<a href="/admin/businessapp/order/?q=&business__username__exact='+str(obj.username)+'"> '+str(obj.order_total2) +'</a>'
    order_total.allow_tags = True
    order_total.admin_order_field='order_total2'

    def total_completed(self,obj):
        return '<a href="/admin/businessapp/order/?q=&business__username__exact='+str(obj.username)+'"> '+str(obj.total_completed2) +'</a>'
    total_completed.allow_tags = True
    total_completed.admin_order_field='total_completed2'

    def order_today(self,obj):

        return '<a href="/admin/businessapp/order/?q=&business__username__exact='+str(obj.username)+'"> '+str(obj.order_today2) +'</a>'
    order_today.allow_tags = True
    order_today.admin_order_field='order_today2'

admin.site.register(Bdheadpanel,BdheadAdmin)



