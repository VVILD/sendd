from django.contrib import admin
from .models import *

from django.http import HttpResponse,HttpResponseRedirect

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
	readonly_fields=('product_info','weight','shipping_cost','generate_order')
	fields = ('product_info','weight','applied_weight' ,'mapped_tracking_no', 'company' ,'shipping_cost','generate_order')
	extra = 0
	def product_info(self,obj):
		return '<b>Name:</b>'+str(obj.name) + '<br>' +'<b>Quantity:</b>'+str(obj.quantity) + '<br>' + 'SKU: '+str(obj.sku )+ '<br>' +'<b>Price:</b>'+str(obj.price )+ '<br>' +"<b>tracking_no:</b>"+str(obj.real_tracking_no )+ '<br>' +"<b>kartrocket_order:</b>"+str(obj.kartrocket_order)
	product_info.allow_tags = True



	def generate_order(self, obj):
		#neworder=GCMDevice.objects.create(registration_id='fdgfdgfdsgfsfdg')
		#device = GCMDevice.objects.get(registration_id='APA91bGKEsBkDFeODXaS0coILc__0qPaWA6etPbK3fiWad2vluI_Q_EQVw9wocFgqCufbJy43PPXxhr7TB2QMx4QSHCgvBoq2l9dzxGRGX0Mnx6V9pPH2p2lAP93XZKyKjVWRu1PIvwd')
		#print "dsa"
		#devicorder.e.send_message("wadhwsdfdsa")
		#print device
		#device = GCMDevice.objects.get(registration_id='APA91bFT-KrRjrc6fWp8KPHDCATa5dgWCmCIARc_ESElyQ2yLKCoVVJAa477on0VtxDaZtvZCAdMerld7lLyr_TW3F3xoUUCqv1zmzr3JnVJrt5EvnoolR2p6J5pgC3ks4jF6o6_5ITE')
		#device.send_message("harsh bahut bada chakka hai.harsh", extra={"tracking_no": "S134807P31","url":"http://128.199.159.90/static/IMG_20150508_144433.jpeg"})
		#device.send_message("harsh bahut bada chakka hai.harsh")
		
		valid=1
		try:
			string=''
			product = Product.objects.get(pk=obj.pk)
			order=product.order
			print order
			error_string=''
			try:
				shipmentid=product.real_tracking_no
				string=string+'shipmentid='+ str(shipmentid)+ '&'
			except:
				valid=0
				error_string=error_string + 'shipmentid not set <br>'

				
			try:
				name=order.name
				if(str(name)!=''):
					string=string+ 'name='+str(name)+ '&'
				else:
					error_string=error_string + 'drop_name not set<br>'
					valid=0

			except:
				valid=0
				error_string=error_string + 'drop_name not set<br>'

			try:
				pname=product.name
				if(str(pname)!=''):
					string=string+ 'pname='+str(pname)+ '&'
				else:
					error_string=error_string + 'item_name not set<br>'
					valid=0
			except:
				print 's'
				error_string=error_string + 'item_name not set<br>'
				valid=0

			try:
				price=product.price

				if(str(price)!='' and str(price)!='None'):
					string=string+ 'price='+str(price)+ '&'
					print "jkjkjkjkjkjkjkjkjkjk"
					print price
					print "jkjkjkjkjkjkjkjkjkjk"	
				else:
					error_string=error_string + 'item_cost not set<br>'
					valid=0
			except:
				print 's'
				error_string=error_string + 'item_cost not set<br>'
				valid=0


			try:
				weight=product.applied_weight
				if(str(weight)!='' and str(weight)!='None'):
					string=string+ 'weight='+str(weight)+ '&'
				else:
					error_string=error_string + 'item_weight not set<br>'
					valid=0

			except:
				print 's'
				error_string=error_string + 'item_weight not set<br>'
				valid=0


			try:
				phone=order.phone
				if(str(phone)!='' and str(phone)!='None'):
					string=string+ 'phone='+str(phone)+ '&'
				else:
					error_string=error_string + 'drop_phone not set<br>'
					valid=0
			except:
				print 's'
				error_string=error_string + 'drop_phone not set<br>'
				valid=0


			try:
				address1=str(order.address1)
				string=string+ 'address='+str(address1)+ '&'
			except:
				print 's'
				error_string=error_string + 'address 1 not set<br>'
				valid=0
			

			try:
				address2=str(order.address2)
				string=string+ 'address1='+str(address2)+ '&'
			except:
				print 's'
				error_string=error_string + 'address 2 not set<br>'
				valid=0
			

			try:
				city=order.city
				string=string+ 'city='+str(city)+ '&'
			except:
				error_string=error_string + 'city not set<br>'
				valid=0				
				print 'k'
			
			try:
				state=order.state
				string=string+ 'state='+str(state)+ '&'
			except:
				error_string=error_string + 'state not set<br>'
				valid=0
				print 's'

			try:
				pincode=order.pincode
				string=string+ 'pincode='+str(pincode)+ '&'
			except:
				error_string=error_string + 'pincode not set<br>'
				valid=0				
				print 's'

						

			#message="Hi " + user.name +", \n Greetings from DoorMint!,Our service provider ' "  + serviceprovider_name + "' (" + serviceprovider_number +") will reach you on "+book_date +" at "+str_time+" for "+ service1_name + "( "+service2_name+"). Call 9022662244, if you need help . Thanks for choosing us!"
			#message=urllib.quote(message)

		except:
			print 's'

		if (valid):
			return 'All good!<br><a href="http://order.sendmates.com/baindex.php?%s" target="_blank" >Create Normal Order</a> <br> <a href="http://order.sendmates.com/cod/?%s" target="_blank" >Create Cod Order</a>' % (string,string)
		else:
			return '<div style="color:red">'+ error_string + '</div>'
	generate_order.allow_tags = True

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

	def response_change(self, request, obj):
		
		#print self.__dict__
		#print request.__dict__
		#print obj.pk
		print "sdddddddddddddddddddddddddddd"
		#return super(UserAdmin, self).response_change(request, obj)
		return HttpResponseRedirect('http://sendmates.com/admin/businessapp/order/'+str(obj.pk) + '/' )

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