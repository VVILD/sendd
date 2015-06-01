from django.contrib import admin
from .models import *
import pdb
import hashlib
from myapp.forms import ShipmentForm
# Register your models here.
from django.http import HttpResponse
from push_notifications.models import APNSDevice, GCMDevice
import urllib

class UserAdmin(admin.ModelAdmin):
	search_fields=['phone','name']
	list_display = ('phone','name','otp','apikey','email','time')
	list_editable = ('name',)

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
	list_display = ('order_no','book_time','code','date','time','full_address','user','name_email','status','way','shipments','send_invoice')
	list_editable = ('date','time','status',)
	list_filter=['book_time','status']



	def full_address(self,obj):
		return str(obj.flat_no)+' '+str(obj.address)+' '+str(obj.pincode)

	def code(self,obj):
		try:
			code=obj.promocode.code
			return '<div style="color:red">%s</div>' % (code)
		except:
			return "no code"
	code.allow_tags = True

	def send_invoice(self,obj):
		valid=1
		e_string=''
		invoice_dict={}
		total=0
		order_no=obj.order_no
		invoice_dict['orderno']=order_no

		try:
			times=Invoicesent.objects.filter(order=obj.order_no)
			times_count=str(times.count()) +' invoices sent'
		except:
			times_count="0 invoices sent"

		try:
			name=obj.namemail.name
			invoice_dict['name']=name
		except:
			e_string=e_string+'name not set <br>'
			valid=0

		try:
			address=obj.address
			invoice_dict['address']=address
		except:
			e_string=e_string+'address not set <br>'
			valid=0

		try:
			email=obj.namemail.email
			invoice_dict['mailto']=email
		except:
			e_string=e_string+'email not set <br>'			

		try:
			book_time=obj.book_time
			invoice_dict['date']=str(book_time)[0:10]
		except:
			e_string=e_string+'time not set <br>'			

		try:
			shipments = Shipment.objects.filter(order=obj.order_no)
			number=shipments.count()
			invoice_dict['numberofshipment']=number
			count=0
			total=0
			for s in shipments:
				try:

					print s.real_tracking_no
					print s.drop_address.pincode
					print s.weight
					print 'check'

					if s.weight is None or s.weight.strip()=='':
						e_string=e_string + str(s.real_tracking_no)+ ' weight not set <br>'
						valid=0
					if s.drop_address.pincode is None:
						e_string=e_string + str(s.real_tracking_no) + ' drop_address pincode not set <br>'
						valid=0
					if s.price is None or s.price.strip()=='':
						e_string=e_string + str(s.real_tracking_no) + ' price not set <br>'
						valid=0

					try:
						invoice_dict['des'+str(count)]= str(s.weight)+ ' kg to ' + str(s.drop_address.pincode)
						invoice_dict['tracking'+str(count)]= str(s.real_tracking_no)
						invoice_dict['price'+str(count)]= str(s.price)
						invoice_dict['total'+str(count)]= str(s.price)
						invoice_dict['quantity'+str(count)]='1'
						total= total + int(s.price)
					except Exception,e:
						print str(e)

					count = count + 1
				except Exception,e:
					print str(e)
					e_string=e_string+'error in fetching shipments <br>'
					valid=0

				invoice_dict['overalltotal']=total				


		except:
			e_string=e_string+'number of xx shipments not set <br>'
			valid=0

		


#			address=obj.address
#			shipments = Shipment.objects.filter(order=obj.order_no)
#			mail_subject="a"
#			mail_content="ggh"
		if (valid):
			return '%s <br> <a target="_blank" href="http://128.199.210.166/test1.php?%s">generate  and send invoice to %s</a>' % (times_count,urllib.urlencode(invoice_dict),invoice_dict['mailto'])
		else:
			return e_string
	send_invoice.allow_tags = True



#http://128.199.210.166/test1.php?name=sargun&address=119%2C+nehru+park&orderno=123&date=12%2F12%2F12&mailto=sargungu%40gmail.com&numberofshipment=1&des0=5+kg+to+400076&des1=1+kg+to+456006&des2=&tracking0=S123433&tracking1=S342423&tracking2=&price0=12&price1=12&price2=&quantity0=1&quantity1=1&quantity2=&total0=12&total1=12&total2=&overalltotal=24&discount=&submit=Submit

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
		return str(i) + '<a href ="http://128.199.159.90/admin/myapp/shipment/?order__order_no=%s" target="_blank" > shipments (click to see) </a>' % (obj.order_no)
	shipments.allow_tags = True

#	<img src="https://farm8.staticflickr.com/7042/6873010155_d4160a32a2_s.jpg" onmouseover="this.width='500'; this.height='500'" onmouseout="this.width='100'; this.height='100'">

admin.site.register(Order,OrderAdmin)
admin.site.register(Gcmmessage)
admin.site.register(Promocode)
admin.site.register(Promocheck)


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
		#print "Ffgd"
		#neworder=GCMDevice.objects.create(registration_id='fdgfdgfdsgfsfdg')
		#device = GCMDevice.objects.get(registration_id='APA91bGKEsBkDFeODXaS0coILc__0qPaWA6etPbK3fiWad2vluI_Q_EQVw9wocFgqCufbJy43PPXxhr7TB2QMx4QSHCgvBoq2l9dzxGRGX0Mnx6V9pPH2p2lAP93XZKyKjVWRu1PIvwd')
		#print "dsa"
		#device.send_message("wadhwsdfdsa")
		#print device
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