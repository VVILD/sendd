from django.contrib import admin
from .models import *
# Register your models here.
class BusinessAdmin(admin.ModelAdmin):
	#search_fields=['name']
	list_display = ('username','business_name','username')
	#list_editable = ('name',)

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User



from django.forms import ModelForm, Textarea ,HiddenInput
from django import forms
from businessapp.models import Product,Order


class BmInline(admin.StackedInline):
    model = BusinessManager
    can_delete = False
    verbose_name_plural = 'businessmanager'

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (BmInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class ProductForm(ModelForm):
	class Meta:
		model = Product
		widgets = {
			'tracking_data': HiddenInput,
			'date': HiddenInput,
		}


admin.site.register(X)

admin.site.register(Business,BusinessAdmin)

admin.site.register(LoginSession)
class ProductAdmin(admin.ModelAdmin):
	#search_fields=['name']
	list_display = ('name','price','weight')
	#list_editable = ('name',)

admin.site.register(Product,ProductAdmin)


admin.site.register(Payment)
admin.site.register(Forgotpass)
admin.site.register(Pricing)

admin.site.register(BusinessManager)


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
	form=ProductForm
	exclude = ['name','quantity','sku','price','weight','real_tracking_no','tracking_data']
	readonly_fields=('product_info','weight','shipping_cost')
	fields = ('product_info','weight','applied_weight' ,'mapped_tracking_no', 'company' ,'shipping_cost')
	extra = 0
	def product_info(self,obj):
		return 'Name:'+str(obj.name) + '<br>' +'Quantity:'+str(obj.quantity) + '<br>' + 'SKU: '+str(obj.sku )+ '<br>' +'Price:'+str(obj.price )+ '<br>' +"tracking_no"+str(obj.real_tracking_no )
	# fieldsets=(
	# ('Basic Information', {'fields':['real_tracking_no','print_invoice',], 'classes':('suit-tab','suit-tab-general')}),
	# 	#('Address', {'fields':['flat_no','address','pincode',], 'classes':('suit-tab','suit-tab-general')}),
	# 	#('Destination Address', {'fields':['drop_name','drop_phone','drop_flat_no','locality','city','state','drop_pincode','country'] , 'classes':['collapse',]})
	# 	#('Invoices',{'fields':['send_invoice',], 'classes':('suit-tab','suit-tab-invoices')})
	# )
	# suit_form_tabs = (('general', 'General'))

	


class OrderAdmin(admin.ModelAdmin):
	inlines=(ProductInline,)
	search_fields=['business__business_name','name']
	list_display = ('order_no','book_time','business_details','name','status','method')
	list_editable = ('status',)
	list_filter=['business','status']


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

	def business_details(self,obj):
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


admin.site.register(Order,OrderAdmin)

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