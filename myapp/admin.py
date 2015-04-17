from django.contrib import admin
from .models import *
import pdb
import hashlib
from myapp.forms import ShipmentForm
# Register your models here.
from django.http import HttpResponse

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

admin.site.register(Address)

class OrderAdmin(admin.ModelAdmin):
	search_fields=['phone','name']
	list_display = ('order_no','book_time','date','time','address','book_user','status','way','shipments')
	list_editable = ('date','time','address','status',)
	list_filter=['date','status','book_time']



	def book_user(self, obj):
		phone=obj.user.pk
		name=obj.user.name
		email=obj.user.email
		return '<a href="/admin/myapp/user/%s/" onclick="return showAddAnotherPopup(this);">%s|%s|%s</a>' % (phone,name,email,phone)
	book_user.allow_tags = True


	def shipments(self, obj):
		shipments = Shipment.objects.filter(order=obj.order_no)
		i=0
		for x in shipments:
			i=i+1
		return str(i) + '<a href ="http://128.199.159.90/admin/myapp/shipment/?q=%s" > shipments (click to see) </a>' % (obj.order_no)
	shipments.allow_tags = True

#	<img src="https://farm8.staticflickr.com/7042/6873010155_d4160a32a2_s.jpg" onmouseover="this.width='500'; this.height='500'" onmouseout="this.width='100'; this.height='100'">

admin.site.register(Order,OrderAdmin)

class ShipmentAdmin(admin.ModelAdmin):
	form=ShipmentForm
	search_fields=['order__order_no',]
	list_display = ('real_tracking_no','name','price','weight','mapped_tracking_no','company','category','drop_phone','drop_name','status','drop_address','img_thumbnail','m_c')
	list_filter=['category']
	list_editable = ('name','price','weight','mapped_tracking_no','company',)
	

	def img_thumbnail(self, obj):
		name=str(obj.img)
		name_mod=name[9:]
		full_url='http://128.199.159.90/static/'+name_mod
		return '<img src="%s" width=60 height=60 onmouseover="this.width=\'500\'; this.height=\'500\'" onmouseout="this.width=\'100\'; this.height=\'100\'" />' % (full_url)
	img_thumbnail.allow_tags = True

	def m_c(self, obj):
		try:
			shipment = Shipment.objects.get(pk=obj.pk)
			address = shipment.drop_address
			string=''
			try:
				orderid=shipment.pk
				string=string+'orderid='+ str(orderid)+ '&'
			except:
				print 's'

				
			try:
				name=shipment.drop_name
				string=string+ 'name='+str(name)+ '&'
			except:
				print 's'

			try:
				pname=shipment.name
				if(str(pname)!=''):
					string=string+ 'pname='+str(pname)+ '&'
			except:
				print 's'

			try:
				price=shipment.price
				if(str(price)!=' '):
					string=string+ 'price='+str(price)+ '&'
			except:
				print 's'
			try:
				weight=shipment.weight
				if(str(weight)!=''):
					string=string+ 'weight='+str(weight)+ '&'
			except:
				print 's'

			try:
				phone=shipment.drop_phone
				string=string+ 'phone='+str(phone)+ '&'
			except:
				print 's'

			try:
				address1=str(address.flat_no) + str (address.locality)
				string=string+ 'address='+str(address1)+ '&'
			except:
				print 's'
			
			try:
				city=address.city
				string=string+ 'city='+str(city)+ '&'
			except:
				print 'k'
			
			try:
				state=address.state
				string=string+ 'state='+str(state)+ '&'
			except:
				print 's'

			try:
				pincode=address.pincode
				string=string+ 'pincode='+str(pincode)+ '&'
			except:
				print 's'

						

			#message="Hi " + user.name +", \n Greetings from DoorMint!,Our service provider ' "  + serviceprovider_name + "' (" + serviceprovider_number +") will reach you on "+book_date +" at "+str_time+" for "+ service1_name + "( "+service2_name+"). Call 9022662244, if you need help . Thanks for choosing us!"
			#message=urllib.quote(message)

		except:
			print 's'

		return '<a href="http://order.sendmates.com/?%s" target="_blank" >C Sms</a>' % (string)
	m_c.allow_tags = True


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