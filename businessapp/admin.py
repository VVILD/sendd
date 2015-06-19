from django.contrib import admin
from .models import *
# Register your models here.
class BusinessAdmin(admin.ModelAdmin):
	#search_fields=['name']
	list_display = ('username','business_name','username')
	#list_editable = ('name',)



from django.forms import ModelForm, Textarea ,HiddenInput
from django import forms
from businessapp.models import Product,Order

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
	readonly_fields=('tatti',)
	fields = ('tatti', 'applied_weight' ,'mapped_tracking_no', 'company' ,'shipping_cost')
	def tatti(self,obj):
		return str(obj.name) + '<br>' + str(obj.quantity) + '<br>' +str(obj.sku )+ '<br>' +str(obj.price )+ '<br>' +str(obj.weight )+ '<br>' +str(obj.real_tracking_no )
	# fieldsets=(
	# ('Basic Information', {'fields':['real_tracking_no','print_invoice',], 'classes':('suit-tab','suit-tab-general')}),
	# 	#('Address', {'fields':['flat_no','address','pincode',], 'classes':('suit-tab','suit-tab-general')}),
	# 	#('Destination Address', {'fields':['drop_name','drop_phone','drop_flat_no','locality','city','state','drop_pincode','country'] , 'classes':['collapse',]})
	# 	#('Invoices',{'fields':['send_invoice',], 'classes':('suit-tab','suit-tab-invoices')})
	# )
	# suit_form_tabs = (('general', 'General'))

	


class OrderAdmin(admin.ModelAdmin):
	inlines=(ProductInline,)





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