from django.contrib import admin
from .models import *
import pdb
import hashlib
from myapp.forms import ShipmentForm
# Register your models here.
from django.http import HttpResponse
from push_notifications.models import APNSDevice, GCMDevice

class UserAdmin(admin.ModelAdmin):
	search_fields=['phone','name']
	list_display = ('phone','name','otp','apikey','email','time')
	list_editable = ('name',)
	def response_change(self, request, obj):
		print self
		print "sdddddddddddddddddddddddddddd"
		#return super(UserAdmin, self).response_change(request, obj)
		return HttpResponse('''
   <script type="text/javascript">
      opener.dismissAddAnotherPopup(window);
   </script>''')

admin.site.register(User,UserAdmin)


class AddressAdmin(admin.ModelAdmin):
	def response_change(self, request, obj):
		print self
		print "sdddddddddddddddddddddddddddd"
		#return super(UserAdmin, self).response_change(request, obj)
		return HttpResponse('''
   <script type="text/javascript">
      opener.dismissAddAnotherPopup(window);
   </script>''')


admin.site.register(Address,AddressAdmin)



class NamemailAdmin(admin.ModelAdmin):
	def response_change(self, request, obj):
		print self
		print "sdddddddddddddddddddddddddddd"
		#return super(UserAdmin, self).response_change(request, obj)
		return HttpResponse('''
   <script type="text/javascript">
      opener.dismissAddAnotherPopup(window);
   </script>''')


admin.site.register(Namemail,NamemailAdmin)


class OrderAdmin(admin.ModelAdmin):
	list_per_page = 10
	search_fields=['user__phone','name','namemail__name','namemail__email']
	list_display = ('order_no','book_time','date','time','address','user','name_email','status','way','shipments')
	list_editable = ('date','time','address','status',)
	list_filter=['book_time','status']



	def name_email(self, obj):
		#pk=obj.namemail.pk
		try:
			pk=obj.namemail.pk
			name=obj.namemail.name
			email=obj.namemail.email
			return '<a href="/admin/myapp/namemail/%s/" onclick="return showAddAnotherPopup(this);">%s|%s</a>' % (pk,name,email)
		except:
			return 'fail'
	name_email.allow_tags = True


	def shipments(self, obj):
		shipments = Shipment.objects.filter(order=obj.order_no)
		i=0
		for x in shipments:
			i=i+1
		return str(i) + '<a href ="http://128.199.159.90/admin/myapp/shipment/?q=%s" target="_blank" > shipments (click to see) </a>' % (obj.order_no)
	shipments.allow_tags = True

#	<img src="https://farm8.staticflickr.com/7042/6873010155_d4160a32a2_s.jpg" onmouseover="this.width='500'; this.height='500'" onmouseout="this.width='100'; this.height='100'">

admin.site.register(Order,OrderAdmin)
admin.site.register(Gcmmessage)


class ShipmentAdmin(admin.ModelAdmin):
	list_per_page = 10
	form=ShipmentForm
	search_fields=['order__order_no','real_tracking_no','mapped_tracking_no','drop_phone','drop_name']
	list_display = ('real_tracking_no','name','cost_of_courier','weight','mapped_tracking_no','company','parcel_details','price','category','drop_phone','drop_name','status','address','generate_order')
	list_filter=['category']
	list_editable = ('name','cost_of_courier','weight','mapped_tracking_no','company','price','category','drop_phone','drop_name',)
	

	def address(self,obj):
		try:
			address=obj.drop_address
			pk=address.pk
			add=str(address.flat_no)+','+str(address.locality)+','+str(address.city)+','+str(address.state)+'-'+str(address.pincode)
			return '<a href="/admin/myapp/address/%s/" onclick="return showAddAnotherPopup(this);">%s</a>' % (pk,add)
		except:
			return "no add"
	address.allow_tags = True


	def parcel_details(self, obj):
		name=str(obj.img)
		print name
		if(name==''):
			return str(obj.item_name)
		name_mod=name[9:]
		full_url='http://128.199.159.90/static/'+name_mod
		return '<img src="%s" width=60 height=60 onmouseover="this.width=\'500\'; this.height=\'500\'" onmouseout="this.width=\'100\'; this.height=\'100\'" />' % (full_url)
	parcel_details.allow_tags = True

	def generate_order(self, obj):
		#neworder=GCMDevice.objects.create(registration_id='fdgfdgfdsgfsfdg')
		try:
			gcmdevice=GCMDevice.objects.filter(registration_id='ADFASFDDSA')
			if (gcmdevice.count()==0) :
				gcmdevice = GCMDevice.objects.create(registration_id='ADFASFDDSA')
			else:
				print "GCM device already exist"
				
		except:
			print "GCM device not created"


		#device = GCMDevice.objects.get(registration_id='APA91bFT-KrRjrc6fWp8KPHDCATa5dgWCmCIARc_ESElyQ2yLKCoVVJAa477on0VtxDaZtvZCAdMerld7lLyr_TW3F3xoUUCqv1zmzr3JnVJrt5EvnoolR2p6J5pgC3ks4jF6o6_5ITE')
		#device.send_message("harsh bahut bada chakka hai.harsh", extra={"tracking_no": "S134807P31","url":"http://128.199.159.90/static/IMG_20150508_144433.jpeg"})
		#device.send_message("harsh bahut bada chakka hai.harsh")
		
		valid=1
		try:
			shipment = Shipment.objects.get(pk=obj.pk)
			address = shipment.drop_address
			string=''
			error_string=''
			try:
				orderid=shipment.pk
				string=string+'orderid='+ str(orderid)+ '&'
			except:
				valid=0
				error_string=error_string + 'orderid not set <br>'

				
			try:
				name=shipment.drop_name
				if(str(name)!=''):
					string=string+ 'name='+str(name)+ '&'
				else:
					error_string=error_string + 'drop_name not set<br>'
					valid=0

			except:
				valid=0
				error_string=error_string + 'drop_name not set<br>'

			try:
				pname=shipment.name
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
				price=shipment.cost_of_courier

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
				weight=shipment.weight
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
				phone=shipment.drop_phone
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
				address1=str(address.flat_no) + str (address.locality)
				string=string+ 'address='+str(address1)+ '&'
			except:
				print 's'
				error_string=error_string + 'address not set<br>'
				valid=0
			
			try:
				city=address.city
				string=string+ 'city='+str(city)+ '&'
			except:
				error_string=error_string + 'city not set<br>'
				valid=0				
				print 'k'
			
			try:
				state=address.state
				string=string+ 'state='+str(state)+ '&'
			except:
				error_string=error_string + 'state not set<br>'
				valid=0
				print 's'

			try:
				pincode=address.pincode
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
			return '<a href="http://order.sendmates.com/?%s" target="_blank" >All good! Create Order</a>' % (string)
		else:
			return '<div style="color:red">'+ error_string + '</div>'
	generate_order.allow_tags = True


admin.site.register(Shipment,ShipmentAdmin)

class XAdmin(admin.ModelAdmin):
	list_display = ('Name','C','thumbnail')

	def thumbnail(self, obj):
		name=str(obj.C)
		name_mod=name[9:]
		full_url='http://128.199.159.90/static/'+name_mod
		return '<img src="%s" width=60 height=60 />' % (full_url)
	thumbnail.allow_tags = True


admin.site.register(X,XAdmin)

admin.site.register(Forgotpass)

class LoginSessionAdmin(admin.ModelAdmin):
	list_display = ('time','success','user')
	list_filter=['time']


admin.site.register(LoginSession,LoginSessionAdmin)

class WeborderAdmin(admin.ModelAdmin):
	list_display = ('item_details','pickup_location','pincode','number','time')

admin.site.register(Weborder,WeborderAdmin)

admin.site.register(Priceapp)