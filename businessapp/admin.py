import urllib
import json
from django.contrib.admin import ModelAdmin, RelatedFieldListFilter

from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from random import randint

import datetime

from django.contrib import admin
from .models import *
from businessapp.forms import NewQcCommentForm,NewTrackingStatus,NewReturnForm
from datetime import date,timedelta
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


from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportActionModelAdmin
import export_xl
import datetime

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


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
		qs = super(CSBusinessAdmin, self).queryset(request)
		qs=qs.filter(daily='True')
		return qs

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
		('General', {'fields': ['name', 'quantity','sku','price','weight','applied_weight','status','date','remittance','order','actual_delivery_timestamp','estimated_delivery_timestamp'], 'classes': ('suit-tab', 'suit-tab-general')}),
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
			obj.status) + '<br>' + "<b>history:</b>" + str(
			obj.tracking_history) + '<br>' + "<b>company:</b>" + str(
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
				return 'All good!<br><a href="/stats/kartrocket/?%s" target="_blank" >Create Kartrocket Normal Order</a>' % (string)
			elif (cod=='C'):
				return 'All good!<br><a href="/stats/kartrocket/?%s" target="_blank" >Create Kartrocket Cod Order</a>' % (string)
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

		if obj.order.fedex_ship_docs:
			return "Print docs from the order view"

		if obj.fedex_ship_docs:
			if obj.order.state == 'Gujarat' and obj.order.method == 'B':
				return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_ship_docs.name).split('/')[-1], "Print Docs")+'<br><br>' + '<br><br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
			else:
				return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_ship_docs.name).split('/')[-1], "Print Docs")+'<br><br>'

		if obj.fedex_outbound_label and obj.fedex_cod_return_label:
			if obj.order.state == 'Gujarat' and obj.order.method == 'B':
				return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label")+'<br><br>'+ '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_cod_return_label.name).split('/')[-1], "Print COD Return Label") + '<br><br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
			else:
				return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label")+'<br><br>'+ '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_cod_return_label.name).split('/')[-1], "Print COD Return Label")
		elif obj.fedex_outbound_label:
			if obj.order.state == 'Gujarat' and obj.order.method == 'B':
				return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label") + '<br><br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
			else:
				return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_outbound_label.name).split('/')[-1], "Print Outbound Label")

		return "Please use the fedex create order link in the order view"
		# if obj.order.state == 'Gujarat' and obj.order.method == 'B':
		#     return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<br> <br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
		#
		# if state_matcher.is_restricted(obj.order.state) and not obj.is_document:
		#     return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<br> <h2 style="color:red">Restricted States</h2>'
		#
		# return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order")

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
		'total_cod_cost', 'method', 'fedex','ff_comment')
	list_editable = ('status','ff_comment',)
	list_filter = ['business', 'status', 'book_time','product__company']
	actions = [export_as_csv_action("CSV Export", fields=['name','product__real_tracking_no'])]
	readonly_fields=('master_tracking_number', 'mapped_master_tracking_number', 'fedex')


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
		if (Product.objects.filter(order=obj).count()==1):
			only_product=Product.objects.get(order=obj)
			if (only_product.company=='F'):
				return '<a href="https://www.fedex.com/apps/fedextrack/?action=track&trackingnumber=%s" target="_blank" >%s</a> ' % (only_product.mapped_tracking_no, only_product.mapped_tracking_no)
			elif (only_product.company=='B'):
				return'<a href="http://www.bluedart.com/servlet/RoutingServlet?handler=tnt&action=awbquery&awb=awb&numbers=%s" target="_blank">%s</a>' % (only_product.mapped_tracking_no, only_product.mapped_tracking_no)
			elif (only_product.mapped_tracking_no and only_product.company ):
				return "1|" + only_product.mapped_tracking_no +"|"+only_product.company
			else:
				return 1
		return Product.objects.filter(order=obj).count()
	no_of_products.allow_tags = True

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

	def fedex(self, obj):
		params = urllib.urlencode({'order_pk': obj.pk, 'client_type': "business"})

		if not obj.state:
			return "Enter state"

		if not state_matcher.is_state(obj.state):
			return '<h2 style="color:red">Enter a valid state</h2>'

		if not obj.pincode:
			return "Enter pincode"

		db_pincode = Pincode.objects.filter(pincode=obj.pincode)

		if db_pincode:
			if not db_pincode[0].fedex_servicable:
				return '<h2 style="color:red">Not Servicable</h2>'
			elif db_pincode[0].fedex_oda_opa:
				return '<h2 style="color:red">ODA</h2>'
		else:
			return '<h2 style="color:red">Enter a valid pincode</h2>'

		if obj.payment_method == 'C':
			if not db_pincode[0].fedex_cod_service:
				return '<h2 style="color:red">Not COD Servicable</h2>'

		is_doc = True
		if obj.product_set.all().count() == 0:
			return "No products"
		for product in obj.product_set.all():
			if not product.applied_weight:
				return "Enter applied weight for %s" % product.name

			if not product.price:
				return "Enter item value for %s" % product.name

			if obj.state == 'West Bengal' and float(product.price) > 1000:
				return '<h2 style="color:red">Product %s is not servicable</h2>' % product.name

			if product.is_document is False:
				is_doc = False

			if product.fedex_ship_docs or product.fedex_outbound_label:
				return "Order already created using legacy"


		if obj.state == 'Kerala' and obj.method == 'B':
			return '<h2 style="color:red">Not Servicable</h2>'

		# Temporary ban
		if obj.state == 'Kerala' and obj.payment_method == 'C':
			return '<h2 style="color:red">Kerala Temporary Ban</h2>'

		if obj.fedex_ship_docs:
			if obj.state == 'Gujarat' and obj.method == 'B':
				return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_ship_docs.name).split('/')[-1], "Print Docs")+'<br><br>' + '<br><br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order") + '<br><br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"
			else:
				return '<a href="/static/%s" target="_blank">%s</a>' % (str(obj.fedex_ship_docs.name).split('/')[-1], "Print Docs")+'<br><br>' + '<br><br><a style="color:red" href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Re-Create Order")

		if obj.state == 'Gujarat' and obj.method == 'B':
			return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<br> <br><a href="http://commercialtax.gujarat.gov.in/vatwebsite/download/form/403.pdf" target="_blank">%s</a>' % "Print Form 403"

		if state_matcher.is_restricted(obj.state) and not is_doc:
			return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order") + '<br> <h2 style="color:red">Restricted States</h2>'

		return '<a href="/create_fedex_shipment/?%s" target="_blank">%s</a>' % (params, "Create Order")

	fedex.allow_tags = True


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


class ProxyProductAdmin(reversion.VersionAdmin):
	
	list_display = ('get_business','sent_to','barcode',)
	search_fields=['order__name',]    
	fieldsets=(
		('Basic Information', {'fields':['barcode',]}),)


	def get_queryset(self, request):
		return self.model.objects.filter(Q(order__business='souled_store')|Q(order__business='snoog'))

	def sent_to(self,obj):
		return obj.order.name
	def get_business(self, obj):
		return obj.order.business
	get_business.short_description = 'business'
	get_business.admin_order_field = 'order__business'


admin.site.register(ProxyProduct, ProxyProductAdmin)    

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


class StatusFilter(admin.SimpleListFilter):
	title = _('trackingstatus')

	parameter_name = 'lts'

	def lookups(self, request, model_admin):

		tracking_set=Product.objects.filter().values("last_tracking_status").annotate(n=Count("pk")).exclude(n__lt=3)
		#tracking_set=Product.objects.filter().values("last_tracking_status").annotate(n=Count("pk"))

		bd_tupel=[]
		club_list=["undelivered","article bagged to","bag despatched", "delivery exception","shipment at delivery location","shipments connected from","transit bag despatched"]
		ignore_list=["delivered","article delivered","bag opened","item delivered"]
		bd_tupel.append(('nbm',_('No tracking status')))
		z=[x for x in tracking_set if x["last_tracking_status"] is not None]
		tracking_set_nonone=[x for x in tracking_set if x["last_tracking_status"] is not None]

		for bd in tracking_set_nonone:
			word= filter(lambda x: bd["last_tracking_status"].lower().startswith(x), club_list)
			if bd["last_tracking_status"]:
				if any(bd["last_tracking_status"].lower().startswith(word) for word in ignore_list):
					pass
				elif len(word):
					if not word[0] in zip(*bd_tupel)[0]:
						bd_tupel.append((word[0],_(word[0])))
				else:
					bd_tupel.append((bd["last_tracking_status"],_(bd["last_tracking_status"])))


		return tuple(bd_tupel)

	def queryset(self, request, queryset):
		print self.value()
		if self.value()==None:
			return queryset.filter()
		if self.value()=='nbm':
			return queryset.filter(last_tracking_status__isnull=True)


		return queryset.filter(last_tracking_status__icontains=self.value())


reversion.VersionAdmin.change_list_template='businessapp/templates/admin/businessapp/change_list.html'



class QcProductAdmin(ProductAdmin,reversion.VersionAdmin,ImportExportActionModelAdmin):

	change_list_template='businessapp/templates/admin/businessapp/qcproduct/change_list.html'

	def get_queryset(self, request):
		return self.model.objects.filter(Q(order__status='DI')| Q(order__status='R')).exclude(Q(status='C')|Q(return_action='R')|Q(return_action='RB')).exclude(order__business='ecell').exclude(order__business='ghasitaram').exclude(order__business='holachef')
	list_display = (
		'order_no','tracking_no','company','book_date','dispatch_time','get_business','sent_to','last_location' ,'expected_delivery_date','last_updated','last_tracking_status','history')
	list_filter = ['order__method','order__business','warning','company',StatusFilter,'status']
	list_editable = ()
	readonly_fields = ('previous_comment','p_tracking')
	search_fields = ['order__order_no', 'real_tracking_no', 'mapped_tracking_no','tracking_data' ]
	

	def save_model(self, request, obj, form, change):
		if obj.qc_comment:
			obj.qc_comment = '\n\n' + str(obj.qc_comment) + '<br>--' + str(request.user) +'(' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ')'
			obj.save()
		else:
			obj.save()


	def get_form(self, request, obj=None, **kwargs):
		#tracking=request.GET.get["tracking",None]
		tracking = request.GET.get('tracking',None)
		status = request.GET.get('status',None)

		if status:
			self.form = NewReturnForm
			self.fieldsets = (
				('Basic Information', {'fields': ['status', 'return_action',], 'classes': ('suit-tab', 'suit-tab-general')}),
			)

		elif not tracking:  #add
			self.form=NewQcCommentForm
			self.fieldsets = (
				('Basic Information', {'fields': ['new_comment', 'previous_comment',], 'classes': ('suit-tab', 'suit-tab-general')}),
				('Basic Information', {'fields': ['qc_comment',], 'classes': ('suit-tab', 'suit-tab-barcode')}),
			)

		elif tracking: #change
			self.form = NewTrackingStatus
			self.fieldsets = (
				('Add new',
				 {'fields': [('tstatus', 'ttime', 'location'), ], 'classes': ('suit-tab', 'suit-tab-general')}),
				('Previous tracking', {'fields': ['p_tracking', ],
									   'classes': ('suit-tab', 'suit-tab-general')}),
				('Do not edit this', {'fields': ['tracking_data', ], 'classes': ('suit-tab', 'suit-tab-tracking')}),
				
			)

			self.suit_form_tabs = (('general', 'General'), ('tracking', 'Tracking'))




		return super(QcProductAdmin, self).get_form(request, obj, **kwargs)

	def response_change(self, request, obj):

		return HttpResponse('''
   <script type="text/javascript">
	  opener.dismissAddAnotherPopup(window);
   </script>''')

	def previous_comment(self,obj):
		return obj.qc_comment

	def p_tracking(self,obj):
		import unicodedata
		json_data=json.loads(obj.tracking_data)
		display_str=''
		for row in json_data:
			display_str=display_str + unicodedata.normalize('NFKD',row["status"] ).encode('ascii', 'ignore') + "&nbsp;&nbsp;&nbsp;&nbsp; " + unicodedata.normalize('NFKD',row["date"] ).encode('ascii', 'ignore') + "&nbsp;&nbsp;&nbsp;&nbsp; " + unicodedata.normalize('NFKD',row["location"] ).encode('ascii', 'ignore') + "<br> <br>"
		return display_str
	p_tracking.allow_tags=True

	def history(self,obj):
		return str(obj.qc_comment) + '<br><br>' + '<a href="/admin/businessapp/qcproduct/%s/" onclick="return showAddAnotherPopup(this);">Add new comment </a><br><a href="/admin/businessapp/qcproduct/%s/?tracking=T" onclick="return showAddAnotherPopup(this);">Add tracking row</a><br> <a href="/admin/businessapp/qcproduct/%s/?status=T" onclick="return showAddAnotherPopup(this);">Return action</a>' % (obj.pk, obj.pk,obj.pk)
	history.allow_tags=True

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

	resource_class=export_xl.QcProductResource


admin.site.register(QcProduct, QcProductAdmin)


def createpricingfieldgeneric(display_name):
	display_name=display_name.replace('_','.')
	type_of_pricing=display_name[0]
	zone=display_name[1]
	weight=display_name[2:]
	if zone=='a':
		name=weight + 'kgs Zone ' + zone 
	else:
		name='Zone ' + zone
	def func1(self,obj):
		y=Pricing2.objects.filter(business=obj,weight__weight=weight,zone__zone=zone,type=type_of_pricing)
		pk_list=[]
		for x in y:
			pk_list.append((x.pk,x.price))
		result_string=  ''
		for item in pk_list:
			result_string= result_string +' <th> <a href="/admin/businessapp/pricing2/'+str(item[0])+'/" onclick="return showAddAnotherPopup(this);"> '+str(item[1]) +'</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </th>'
		return result_string
	func1.__name__ = display_name
	func1.short_description = _(name)
	return func1

def createpricingfieldgeneric2(display_name):
	display_name=display_name.replace('_','.')
	type_of_pricing=display_name[0]
	zone=display_name[1]
	weight=display_name[2:]
	if zone=='a':
		name=weight + 'kgs Zone ' + zone 
	else:
		name='Zone ' + zone
	def func1(self,obj):
		y=Pricing2.objects.filter(business=obj,weight__weight=weight,zone__zone=zone,type=type_of_pricing)
		pk_list=[]
		for x in y:
			pk_list.append((x.pk,x.ppkg))
		result_string=  ''
		for item in pk_list:
			result_string= result_string +' <th> <a href="/admin/businessapp/pricing2/'+str(item[0])+'/?ppk=True" onclick="return showAddAnotherPopup(this);"> '+str(item[1]) +'</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; </th>'
		return result_string
	func1.__name__ = display_name
	func1.short_description = _(name)
	return func1


class BusinessPricingAdmin(reversion.VersionAdmin):
	list_filter=('username','business_name')
	list_display=('business_name',)
#    readonly_fields=('N0_25','N0_5','N1','N2','N3','N4','N5','N6','N7','N8','N9','N10','B1','B2','B3','B4','B5','B6','B7','B8','B9','B10')
	readonly_fields=('Na0_25','Nb0_25','Nc0_25','Nd0_25','Ne0_25','Na0_5','Nb0_5','Nc0_5','Nd0_5','Ne0_5',
		'Na1','Nb1','Nc1','Nd1','Ne1','Na1_5','Nb1_5','Nc1_5','Nd1_5','Ne1_5',
		'Na2','Nb2','Nc2','Nd2','Ne2','Na2_5','Nb2_5','Nc2_5','Nd2_5','Ne2_5',
		'Na3','Nb3','Nc3','Nd3','Ne3','Na3_5','Nb3_5','Nc3_5','Nd3_5','Ne3_5',
		'Na4','Nb4','Nc4','Nd4','Ne4','Na4_5','Nb4_5','Nc4_5','Nd4_5','Ne4_5',
		'Na5','Nb5','Nc5','Nd5','Ne5','Na5_5','Nb5_5','Nc5_5','Nd5_5','Ne5_5',
		'Na6','Nb6','Nc6','Nd6','Ne6','Na6_5','Nb6_5','Nc6_5','Nd6_5','Ne6_5',
		'Na7','Nb7','Nc7','Nd7','Ne7','Na7_5','Nb7_5','Nc7_5','Nd7_5','Ne7_5',
		'Na8','Nb8','Nc8','Nd8','Ne8','Na8_5','Nb8_5','Nc8_5','Nd8_5','Ne8_5',
		'Na9','Nb9','Nc9','Nd9','Ne9','Na9_5','Nb9_5','Nc9_5','Nd9_5','Ne9_5',
		'Na10','Nb10','Nc10','Nd10','Ne10','Na11','Nb11','Nc11','Nd11','Ne11',
		'Ba1','Bb1','Bc1','Bd1','Be1',
		'Ba2','Bb2','Bc2','Bd2','Be2',
		'Ba3','Bb3','Bc3','Bd3','Be3',
		'Ba4','Bb4','Bc4','Bd4','Be4',
		'Ba5','Bb5','Bc5','Bd5','Be5',
		'Ba6','Bb6','Bc6','Bd6','Be6',
		'Ba7','Bb7','Bc7','Bd7','Be7',
		'Ba8','Bb8','Bc8','Bd8','Be8',
		'Ba9','Bb9','Bc9','Bd9','Be9',
		'Ba10','Bb10','Bc10','Bd10','Be10',
		'Ba11','Bb11','Bc11','Bd11','Be11',)

	Na0_25=createpricingfieldgeneric('Na0_25')
	Nb0_25=createpricingfieldgeneric('Nb0_25')
	Nc0_25=createpricingfieldgeneric('Nc0_25')
	Nd0_25=createpricingfieldgeneric('Nd0_25')
	Ne0_25=createpricingfieldgeneric('Ne0_25')

	Na0_5=createpricingfieldgeneric('Na0_5')
	Nb0_5=createpricingfieldgeneric('Nb0_5')
	Nc0_5=createpricingfieldgeneric('Nc0_5')
	Nd0_5=createpricingfieldgeneric('Nd0_5')
	Ne0_5=createpricingfieldgeneric('Ne0_5')


	Na1=createpricingfieldgeneric('Na1')
	Nb1=createpricingfieldgeneric('Nb1')
	Nc1=createpricingfieldgeneric('Nc1')
	Nd1=createpricingfieldgeneric('Nd1')
	Ne1=createpricingfieldgeneric('Ne1')

	Na1_5=createpricingfieldgeneric('Na1_5')
	Nb1_5=createpricingfieldgeneric('Nb1_5')
	Nc1_5=createpricingfieldgeneric('Nc1_5')
	Nd1_5=createpricingfieldgeneric('Nd1_5')
	Ne1_5=createpricingfieldgeneric('Ne1_5')

	Na2=createpricingfieldgeneric('Na2')
	Nb2=createpricingfieldgeneric('Nb2')
	Nc2=createpricingfieldgeneric('Nc2')
	Nd2=createpricingfieldgeneric('Nd2')
	Ne2=createpricingfieldgeneric('Ne2')

	Na2_5=createpricingfieldgeneric('Na2_5')
	Nb2_5=createpricingfieldgeneric('Nb2_5')
	Nc2_5=createpricingfieldgeneric('Nc2_5')
	Nd2_5=createpricingfieldgeneric('Nd2_5')
	Ne2_5=createpricingfieldgeneric('Ne2_5')

	Na3=createpricingfieldgeneric('Na3')
	Nb3=createpricingfieldgeneric('Nb3')
	Nc3=createpricingfieldgeneric('Nc3')
	Nd3=createpricingfieldgeneric('Nd3')
	Ne3=createpricingfieldgeneric('Ne3')

	Na3_5=createpricingfieldgeneric('Na3_5')
	Nb3_5=createpricingfieldgeneric('Nb3_5')
	Nc3_5=createpricingfieldgeneric('Nc3_5')
	Nd3_5=createpricingfieldgeneric('Nd3_5')
	Ne3_5=createpricingfieldgeneric('Ne3_5')

	Na4=createpricingfieldgeneric('Na4')
	Nb4=createpricingfieldgeneric('Nb4')
	Nc4=createpricingfieldgeneric('Nc4')
	Nd4=createpricingfieldgeneric('Nd4')
	Ne4=createpricingfieldgeneric('Ne4')

	Na4_5=createpricingfieldgeneric('Na4_5')
	Nb4_5=createpricingfieldgeneric('Nb4_5')
	Nc4_5=createpricingfieldgeneric('Nc4_5')
	Nd4_5=createpricingfieldgeneric('Nd4_5')
	Ne4_5=createpricingfieldgeneric('Ne4_5')

	Na5=createpricingfieldgeneric('Na5')
	Nb5=createpricingfieldgeneric('Nb5')
	Nc5=createpricingfieldgeneric('Nc5')
	Nd5=createpricingfieldgeneric('Nd5')
	Ne5=createpricingfieldgeneric('Ne5')

	Na5_5=createpricingfieldgeneric('Na5_5')
	Nb5_5=createpricingfieldgeneric('Nb5_5')
	Nc5_5=createpricingfieldgeneric('Nc5_5')
	Nd5_5=createpricingfieldgeneric('Nd5_5')
	Ne5_5=createpricingfieldgeneric('Ne5_5')

	Na6=createpricingfieldgeneric('Na6')
	Nb6=createpricingfieldgeneric('Nb6')
	Nc6=createpricingfieldgeneric('Nc6')
	Nd6=createpricingfieldgeneric('Nd6')
	Ne6=createpricingfieldgeneric('Ne6')

	Na6_5=createpricingfieldgeneric('Na6_5')
	Nb6_5=createpricingfieldgeneric('Nb6_5')
	Nc6_5=createpricingfieldgeneric('Nc6_5')
	Nd6_5=createpricingfieldgeneric('Nd6_5')
	Ne6_5=createpricingfieldgeneric('Ne6_5')

	Na7=createpricingfieldgeneric('Na7')
	Nb7=createpricingfieldgeneric('Nb7')
	Nc7=createpricingfieldgeneric('Nc7')
	Nd7=createpricingfieldgeneric('Nd7')
	Ne7=createpricingfieldgeneric('Ne7')

	Na7_5=createpricingfieldgeneric('Na7_5')
	Nb7_5=createpricingfieldgeneric('Nb7_5')
	Nc7_5=createpricingfieldgeneric('Nc7_5')
	Nd7_5=createpricingfieldgeneric('Nd7_5')
	Ne7_5=createpricingfieldgeneric('Ne7_5')

	Na8=createpricingfieldgeneric('Na8')
	Nb8=createpricingfieldgeneric('Nb8')
	Nc8=createpricingfieldgeneric('Nc8')
	Nd8=createpricingfieldgeneric('Nd8')
	Ne8=createpricingfieldgeneric('Ne8')

	Na8_5=createpricingfieldgeneric('Na8_5')
	Nb8_5=createpricingfieldgeneric('Nb8_5')
	Nc8_5=createpricingfieldgeneric('Nc8_5')
	Nd8_5=createpricingfieldgeneric('Nd8_5')
	Ne8_5=createpricingfieldgeneric('Ne8_5')

	Na9=createpricingfieldgeneric('Na9')
	Nb9=createpricingfieldgeneric('Nb9')
	Nc9=createpricingfieldgeneric('Nc9')
	Nd9=createpricingfieldgeneric('Nd9')
	Ne9=createpricingfieldgeneric('Ne9')

	Na9_5=createpricingfieldgeneric('Na9_5')
	Nb9_5=createpricingfieldgeneric('Nb9_5')
	Nc9_5=createpricingfieldgeneric('Nc9_5')
	Nd9_5=createpricingfieldgeneric('Nd9_5')
	Ne9_5=createpricingfieldgeneric('Ne9_5')

	Na10=createpricingfieldgeneric('Na10')
	Nb10=createpricingfieldgeneric('Nb10')
	Nc10=createpricingfieldgeneric('Nc10')
	Nd10=createpricingfieldgeneric('Nd10')
	Ne10=createpricingfieldgeneric('Ne10')

	Na11=createpricingfieldgeneric2('Na11')
	Nb11=createpricingfieldgeneric2('Nb11')
	Nc11=createpricingfieldgeneric2('Nc11')
	Nd11=createpricingfieldgeneric2('Nd11')
	Ne11=createpricingfieldgeneric2('Ne11')


	Ba1=createpricingfieldgeneric('Ba1')
	Bb1=createpricingfieldgeneric('Bb1')
	Bc1=createpricingfieldgeneric('Bc1')
	Bd1=createpricingfieldgeneric('Bd1')
	Be1=createpricingfieldgeneric('Be1')

	Ba2=createpricingfieldgeneric('Ba2')
	Bb2=createpricingfieldgeneric('Bb2')
	Bc2=createpricingfieldgeneric('Bc2')
	Bd2=createpricingfieldgeneric('Bd2')
	Be2=createpricingfieldgeneric('Be2')

	Ba3=createpricingfieldgeneric('Ba3')
	Bb3=createpricingfieldgeneric('Bb3')
	Bc3=createpricingfieldgeneric('Bc3')
	Bd3=createpricingfieldgeneric('Bd3')
	Be3=createpricingfieldgeneric('Be3')

	Ba4=createpricingfieldgeneric('Ba4')
	Bb4=createpricingfieldgeneric('Bb4')
	Bc4=createpricingfieldgeneric('Bc4')
	Bd4=createpricingfieldgeneric('Bd4')
	Be4=createpricingfieldgeneric('Be4')

	Ba5=createpricingfieldgeneric('Ba5')
	Bb5=createpricingfieldgeneric('Bb5')
	Bc5=createpricingfieldgeneric('Bc5')
	Bd5=createpricingfieldgeneric('Bd5')
	Be5=createpricingfieldgeneric('Be5')

	Ba6=createpricingfieldgeneric('Ba6')
	Bb6=createpricingfieldgeneric('Bb6')
	Bc6=createpricingfieldgeneric('Bc6')
	Bd6=createpricingfieldgeneric('Bd6')
	Be6=createpricingfieldgeneric('Be6')

	Ba7=createpricingfieldgeneric('Ba7')
	Bb7=createpricingfieldgeneric('Bb7')
	Bc7=createpricingfieldgeneric('Bc7')
	Bd7=createpricingfieldgeneric('Bd7')
	Be7=createpricingfieldgeneric('Be7')

	Ba8=createpricingfieldgeneric('Ba8')
	Bb8=createpricingfieldgeneric('Bb8')
	Bc8=createpricingfieldgeneric('Bc8')
	Bd8=createpricingfieldgeneric('Bd8')
	Be8=createpricingfieldgeneric('Be8')

	Ba9=createpricingfieldgeneric('Ba9')
	Bb9=createpricingfieldgeneric('Bb9')
	Bc9=createpricingfieldgeneric('Bc9')
	Bd9=createpricingfieldgeneric('Bd9')
	Be9=createpricingfieldgeneric('Be9')

	Ba10=createpricingfieldgeneric('Ba10')
	Bb10=createpricingfieldgeneric('Bb10')
	Bc10=createpricingfieldgeneric('Bc10')
	Bd10=createpricingfieldgeneric('Bd10')
	Be10=createpricingfieldgeneric('Be10')

	Ba11=createpricingfieldgeneric2('Ba11')
	Bb11=createpricingfieldgeneric2('Bb11')
	Bc11=createpricingfieldgeneric2('Bc11')
	Bd11=createpricingfieldgeneric2('Bd11')
	Be11=createpricingfieldgeneric2('Be11')



	fieldsets = (
		('Normal Pricing', {'fields': [
('Na0_25','Nb0_25','Nc0_25','Nd0_25','Ne0_25'),('Na0_5','Nb0_5','Nc0_5','Nd0_5','Ne0_5'),
		('Na1','Nb1','Nc1','Nd1','Ne1'),('Na1_5','Nb1_5','Nc1_5','Nd1_5','Ne1_5'),
		('Na2','Nb2','Nc2','Nd2','Ne2'),('Na2_5','Nb2_5','Nc2_5','Nd2_5','Ne2_5'),
		('Na3','Nb3','Nc3','Nd3','Ne3'),('Na3_5','Nb3_5','Nc3_5','Nd3_5','Ne3_5'),
		('Na4','Nb4','Nc4','Nd4','Ne4'),('Na4_5','Nb4_5','Nc4_5','Nd4_5','Ne4_5'),
		('Na5','Nb5','Nc5','Nd5','Ne5'),('Na5_5','Nb5_5','Nc5_5','Nd5_5','Ne5_5'),
		('Na6','Nb6','Nc6','Nd6','Ne6'),('Na6_5','Nb6_5','Nc6_5','Nd6_5','Ne6_5'),
		('Na7','Nb7','Nc7','Nd7','Ne7'),('Na7_5','Nb7_5','Nc7_5','Nd7_5','Ne7_5'),
		('Na8','Nb8','Nc8','Nd8','Ne8'),('Na8_5','Nb8_5','Nc8_5','Nd8_5','Ne8_5'),
		('Na9','Nb9','Nc9','Nd9','Ne9'),('Na9_5','Nb9_5','Nc9_5','Nd9_5','Ne9_5'),
		('Na10','Nb10','Nc10','Nd10','Ne10'),('Na11','Nb11','Nc11','Nd11','Ne11')
			]}),
		('Bulk Pricing', {'fields': [
('Ba1','Bb1','Bc1','Bd1','Be1'),
		('Ba2','Bb2','Bc2','Bd2','Be2'),
		('Ba3','Bb3','Bc3','Bd3','Be3'),
		('Ba4','Bb4','Bc4','Bd4','Be4'),
		('Ba5','Bb5','Bc5','Bd5','Be5'),
		('Ba6','Bb6','Bc6','Bd6','Be6'),
		('Ba7','Bb7','Bc7','Bd7','Be7'),
		('Ba8','Bb8','Bc8','Bd8','Be8'),
		('Ba9','Bb9','Bc9','Bd9','Be9'),
		('Ba10','Bb10','Bc10','Bd10','Be10'),
		('Ba11','Bb11','Bc11','Bd11','Be11'),
			]}),
		('Cod Pricing', {'fields': [('cod_sum','cod_percentage'),'discount_percentage']}),
		# ('Bulk Pricing',
		#  {'fields': [('name', 'weight', 'cost_of_courier'), ], 'classes': ('suit-tab', 'suit-tab-general')}),
	)

admin.site.register(BusinessPricing,BusinessPricingAdmin)


class ExportOrderAdmin(ImportExportActionModelAdmin):

	def lookup_allowed(self,key,value):
		return True

	list_filter=('order__business__business_name','order__business__username','order__book_time','last_tracking_status','company','status','remittance','order__payment_method','order__status')
	search_fields = ['name', 'real_tracking_no','order__business__business_name','order__business__username','order__order_no']
	list_display = ('order_no','get_business', 'status', 'applied_weight', 'real_tracking_no', 'barcode','date','last_tracking_status','mapped_tracking_no' ,'company','payment_method','remittance')


	def payment_method(self, obj):
		try:
			return obj.order.payment_method
		except:
			return "None"


	def order_no(self, obj):
		try:
			return '<a href="/admin/businessapp/order/%s/">%s</a>' % (obj.order.pk, obj.order.pk)
		except:
			return 'None'
	order_no.allow_tags = True
	order_no.admin_order_field = 'order'

	def get_business(self, obj):
		try:
			return obj.order.business
		except:
			return "None"

	get_business.short_description = 'business'
	get_business.admin_order_field = 'order__business'
	readonly_fields = (
		'name', 'quantity', 'sku', 'price', 'weight', 'applied_weight', 'real_tracking_no', 'order',
		'kartrocket_order', 'shipping_cost', 'cod_cost', 'status', 'date', 'barcode')

	resource_class=export_xl.ProductResource



admin.site.register(ExportOrder,ExportOrderAdmin)

class Pricing2Admin(admin.ModelAdmin):
	# search_fields=['name']
	list_filter=('business__username','business__business_name','zone','weight','type')
	list_display=('business',)

	def response_change(self, request, obj):
		print "rrrrrrrrrreturning  "
		return HttpResponse('''
   <script type="text/javascript">
	  opener.dismissAddAnotherPopup(window);
   </script>''')

	readonly_fields=('ppkg','weight','zone','type','business')
	def get_form(self, request, obj=None, **kwargs):
		#tracking=request.GET.get["tracking",None]
		ppkg = request.GET.get('ppkg',None)
		
		if ppkg:
			self.readonly_fields=('price','weight','zone','type','business')

		else:
			self.readonly_fields=('ppkg','weight','zone','type','business')


		return super(Pricing2Admin, self).get_form(request, obj, **kwargs)


	


admin.site.register(Pricing2,Pricing2Admin)


class WeightAdmin(reversion.VersionAdmin):
	pass

admin.site.register(Weight,WeightAdmin)

class ZoneAdmin(reversion.VersionAdmin):
	pass

admin.site.register(Zone,ZoneAdmin)





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
		todays_date=datetime.date.today()
		date_max = datetime.datetime.combine(todays_date, datetime.time.max)
		date_min = datetime.datetime.combine(todays_date, datetime.time.min)

		try:
			start_time=request.GET['order__book_time__gte']
			end_time=request.GET['order__book_time__lte']
		

		except:
			start_time= date(2015,1,1)
			end_time=date.today() + datetime.timedelta(days=2)
#'order_total','order_today','total_completed','total_revenue',

		return Business.objects.extra(select={
			'order_total2': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.book_time BETWEEN %s AND %s",
			'total_completed2': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.status='C' and businessapp_order.book_time BETWEEN %s AND %s",
			'order_today2': "SELECT COUNT(businessapp_order.status) from businessapp_order where businessapp_order.business_id = businessapp_business.username and businessapp_order.book_time BETWEEN %s AND %s",},
			select_params=(date_min,date_max,start_time,end_time,start_time,end_time,),
			)
	search_fields=['username','business_name']
	list_display = ('username','business_name', 'warehouse', 'businessmanager','order_total','order_today','total_completed','total_revenue')
	#aw_id_fields = ('pb', 'warehouse')
	list_filter = ['warehouse',BmFilter,('order__book_time', DateRangeFilter),]


	actions = [export_as_csv_action("CSV Export", fields=['username','business_name','apikey','name','email','contact_mob','contact_office','address','city','state','pincode'])]
	actions_on_bottom = False
	actions_on_top = True

	def changelist_view(self, request, extra_context=None):

		try:
			start_time=request.GET['order__book_time__gte']
			end_time=request.GET['order__book_time__lte']
			start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
			end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
		except:
			start_time= datetime.date(2015,1,1)
			end_time=datetime.date.today() + datetime.timedelta(days=2)

		try:
			start_min = datetime.datetime.combine(start_time, datetime.time.min)
			end_max = datetime.datetime.combine(end_time, datetime.time.max)

			bd_username= request.GET['decade']
			profile=Profile.objects.get(user__username=bd_username)
			today_orders_b2b = Order.objects.filter(business__businessmanager=profile,book_time__range=(start_min, end_max))
			today_products_correct = Product.objects.filter(order=today_orders_b2b).exclude(shipping_cost__isnull=True)
			sum_b2b = today_products_correct.aggregate(total=Sum('shipping_cost', field="shipping_cost+cod_cost"))['total']
			count_b2b = today_products_correct.count()

		except:
			bd_username=None
			sum_b2b=0
			count_b2b=0
			today_orders_b2b = Order.objects.filter(book_time__range=(start_min, end_max))
			today_products_correct = Product.objects.filter(order=today_orders_b2b)
			sum_b2b = today_products_correct.aggregate(total=Sum('shipping_cost', field="shipping_cost+cod_cost"))['total']
			count_b2b = today_products_correct.count()


		context={'s':sum_b2b,'c':count_b2b}

		return super(BdheadAdmin, self).changelist_view(request, extra_context=context)

	def total_revenue(self,obj):
		today_orders_b2b = Order.objects.filter(business=obj.username)
		today_products_correct = Product.objects.filter(order=today_orders_b2b).exclude(shipping_cost__isnull=True)
		sum_b2b = today_products_correct.aggregate(total=Sum('shipping_cost', field="shipping_cost+cod_cost"))['total']
		count_b2b = today_products_correct.count()


		return str(sum_b2b)+'|' + str(count_b2b)

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



