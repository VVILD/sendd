from tastypie.resources import ModelResource
from django.conf.urls import url
from businessapp.models import *
from tastypie.authorization import Authorization
from tastypie import fields
from tastypie.serializers import Serializer
from random import randint
import random
import urllib2,urllib
import hashlib, random
import os
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.authentication import ApiKeyAuthentication
import math
import string
from django.core.mail import send_mail
from push_notifications.models import APNSDevice, GCMDevice
import ast
import json
from tastypie.resources import Resource
from tastypie.fields import ListField


from tastypie.authentication import Authentication


# class SillyAuthentication(Authentication):
#     def is_authenticated(self, request, **kwargs):
        
#         print self.__dict__
#         print request.__dict__
#         if 'daniel' in request.user.username:
#           return True

#         return False


from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized


class OnlyAuthorization(Authorization):

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        print "0kkkkkkkkkkkkkkkk"
        print bundle.request.META["HTTP_AUTHORIZATION"]
        print bundle.obj.business.apikey
        return bundle.request.META["HTTP_AUTHORIZATION"]==bundle.obj.business.apikey

    def create_list(self, object_list, bundle):
        # Assuming they're auto-assigned to ``user``.
        print '1kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk'
        return object_list

    def create_detail(self, object_list, bundle):
    	print '2kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk'
        return bundle.obj.user == bundle.request.user

    def update_list(self, object_list, bundle):
        allowed = []

        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        return bundle.obj.user == bundle.request.user

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


'''
Add CORS headers for tastypie APIs

Usage:
   class MyModelResource(CORSModelResource):
	   ...
	   
   class MyResource(CORSResource):
	   ...
	   
Authors:
   original source by http://codeispoetry.me/index.php/make-your-django-tastypie-api-cross-domain/
   extensions by @miraculixx
   * deal with ?format requests
   * always return CORS headers, even if always_return_data is False
   * handle exceptions properly (e.g. raise tastypie.BadRequests) 
   * provide two distinct classes for ModelResource and Resource classes
'''
from django.http.response import HttpResponse
from tastypie import http
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.resources import csrf_exempt
from tastypie.resources import Resource, ModelResource
import logging

class BaseCorsResource(Resource):
	"""
	Class implementing CORS
	"""
	def error_response(self, *args, **kwargs):
		response = super(BaseCorsResource, self).error_response(*args, **kwargs)
		return self.add_cors_headers(response, expose_headers=True)
		
	def add_cors_headers(self, response, expose_headers=False):
		response['Access-Control-Allow-Origin'] = '*'
		response['Access-Control-Allow-Headers'] = 'content-type, authorization, x-requested-with, x-csrftoken'
		if expose_headers:
			response['Access-Control-Expose-Headers'] = 'Location'
		return response    
	
	def create_response(self, *args, **kwargs):
		"""
		Create the response for a resource. Note this will only
		be called on a GET, POST, PUT request if 
		always_return_data is True
		"""
		response = super(BaseCorsResource, self).create_response(*args, **kwargs)
		return self.add_cors_headers(response)

	def post_list(self, request, **kwargs):
		"""
		In case of POST make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
		#logger.debug("post list %s\n%s" % (request, kwargs));
		response = super(BaseCorsResource, self).post_list(request, **kwargs)
		return self.add_cors_headers(response, True)
	
	def post_detail(self, request, **kwargs):
		"""
		In case of POST make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
		#logger.debug("post detail %s\n%s" (request, **kwargs));
		response = super(BaseCorsResource, self).post_list(request, **kwargs)
		return self.add_cors_headers(response, True)
	
	def put_list(self, request, **kwargs):
		"""
		In case of PUT make sure we return the Access-Control-Allow Origin
		regardless of returning data
		"""
		response = super(BaseCorsResource, self).put_list(request, **kwargs)
		return self.add_cors_headers(response, True)    
	
	def put_detail(self, request, **kwargs):
		response = super(BaseCorsResource, self).put_detail(request, **kwargs)
		return self.add_cors_headers(response, True)
		
	def method_check(self, request, allowed=None):
		"""
		Check for an OPTIONS request. If so return the Allow- headers
		"""
		if allowed is None:
			allowed = []
			
		request_method = request.method.lower()
		allows = ','.join(map(lambda s: s.upper(), allowed))

		if request_method == 'options':
			response = HttpResponse(allows)
			response['Access-Control-Allow-Origin'] = '*'
			response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, X-CSRFToken, X-HTTP-Method-Override'
			response['Access-Control-Allow-Methods'] = "GET, PUT, POST, PATCH"
			response['Allow'] = allows
			raise ImmediateHttpResponse(response=response)

		if not request_method in allowed:
			response = http.HttpMethodNotAllowed(allows)
			response['Allow'] = allows
			raise ImmediateHttpResponse(response=response)

		return request_method
	
	def wrap_view(self, view):
		@csrf_exempt
		def wrapper(request, *args, **kwargs):
			request.format = kwargs.pop('format', None)
			wrapped_view = super(BaseCorsResource, self).wrap_view(view)
			return wrapped_view(request, *args, **kwargs)
		return wrapper

#Base Extended Abstract Model
class CORSModelResource(BaseCorsResource, ModelResource):
	pass

class CORSResource(BaseCorsResource, Resource):
	pass

class MultipartResource(object):
	def deserialize(self, request, data, format=None):
		if not format:
			format = request.META.get('CONTENT_TYPE', 'application/json')

		if format == 'application/x-www-form-urlencoded':
			return request.POST

		if format.startswith('multipart'):
			data = request.POST.copy()
			data.update(request.FILES)

			return data

		return super(MultipartResource, self).deserialize(request, data, format)




class BusinessResource(CORSModelResource):
	class Meta:
		queryset = Business.objects.all()
		resource_name = 'business'
		excludes = ['password']
		authorization= Authorization()
		always_return_data = True

	def dehydrate(self,bundle):
		bundle.data['manager']='sargun gulati'
		bundle.data['manager_number']='8879006197'

		return bundle
	# def hydrate(self,bundle):
	# 	try:
	# 		business=Business.objects.get(pk=bundle.data['username'])
	# 		bundle.data["username"]='0'
	# 		bundle.data["msg"]='Username exist'
	# 		return bundle
	# 	except:
	# 		print "fuck"
	# 		bundle.data["msg"]='business created'
	# 		return bundle





class BillingResource(CORSModelResource):
	business = fields.ForeignKey(BusinessResource, 'business' ,null=True)
	class Meta:
		queryset = Billing.objects.all()
		resource_name = 'billing'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):

		bundle.data["cost"]='200'
		bundle.data["paid"]='100'
		bundle.data["due"]='100'
				

		return bundle


class PaymentResource(CORSModelResource):
	business = fields.ForeignKey(BusinessResource, 'business' ,null=True)
	class Meta:
		queryset = Payment.objects.all()
		list_allowed_methods = ['get']
		detail_allowed_methods = ['get']
		resource_name = 'payment'
		authorization= Authorization()
		always_return_data = True

	def build_filters(self, filters=None):
		print "shit"
		print filters
		if filters is None:
			filters = {}
		orm_filters = super(PaymentResource, self).build_filters(filters)

		if 'q' in filters:
			orm_filters['q'] = filters['q']
		return orm_filters

	def apply_filters(self, request, orm_filters):
		base_object_list = super(PaymentResource, self).apply_filters(request, {})
		print orm_filters
		if 'q' in orm_filters:
			return base_object_list.filter(business__username=orm_filters['q'])
		print base_object_list
		return base_object_list



class UsernamecheckResource(CORSModelResource):
	class Meta:
		queryset = Usernamecheck.objects.all()
		resource_name = 'usernamecheck'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			business=Business.objects.get(pk=bundle.data['username'])
			bundle.data["exist"]='Y'
			return bundle
		except:
			bundle.data["exist"]='N'
			return bundle

class LoginSessionResource(CORSModelResource):
	business = fields.ForeignKey(BusinessResource, 'business' ,null=True)
	class Meta:
		queryset = LoginSession.objects.all()
		resource_name = 'loginsession'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			business=Business.objects.get(pk=bundle.data['username'])
		except:
			print "fuck"
			bundle.data["msg"]='notregistered'
			return bundle

		password=business.password
		bundle.data['business']="/bapi/v1/business/"+str(bundle.data['username'])+"/"
		
		
		if (bundle.data['password']== password):
			bundle.data["msg"]='success'
			bundle.data['name']=business.name
			bundle.data['manager']='sargun gulati'
			bundle.data['manager_number']='8879006197'



		#print bundle.data['user']
		#print bundle.data['password']
		return bundle

	def dehydrate(self,bundle):
	#	bundle.data['manager']='sargun gulati'
	#	bundle.data['manager_number']='8879006197'
		bundle.data['password']=''

		return bundle


class OrderResource(CORSModelResource):
	business = fields.ForeignKey(BusinessResource, 'business' ,null=True)
	products = ListField(attribute='products',null=True)
	class Meta:
		queryset = Order.objects.all()
		resourcese_name = 'order'
		authorization=OnlyAuthorization()
	#	authentication=Authentication()
		always_return_data = True


	def build_filters(self, filters=None):
		print "shit"
		print filters
		if filters is None:
			filters = {}
		orm_filters = super(OrderResource, self).build_filters(filters)

		if 'q' in filters:
			orm_filters['q'] = filters['q']
		return orm_filters

	def apply_filters(self, request, orm_filters):
		base_object_list = super(OrderResource, self).apply_filters(request, {})
		print orm_filters
		if 'q' in orm_filters:
			return base_object_list.filter(business__username=orm_filters['q']).exclude(status='N')
		print base_object_list
		return base_object_list


	def hydrate(self,bundle):
		try:
			override_method=bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
			print "changed to PATCH"
		except:
			override_method='none'
			print "hello"
			
		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method=='PATCH':
			print "patch"
			return bundle

	def dehydrate(self,bundle):
		try:
			pk=bundle.data['resource_uri'].split('/')[4]
			order=Order.objects.get(pk=pk)
			product=Product.objects.filter(order=order)
			print product
			l=[]
			for p in product:
				product_name=p.name
				product_quantity=p.quantity
				print '1'
				product_weight=p.weight
				product_applied_weight=p.applied_weight
				product_price=p.price
				product_shipping_cost=p.shipping_cost
				product_sku=p.sku
				product_trackingid=p.real_tracking_no
				
				
				print '2'

				tracking_json=json.loads(p.tracking_data)
				print '3'
				product_status=tracking_json[-1]['status'].encode('ascii','ignore')
				product_date=tracking_json[-1]['date'].encode('ascii','ignore')
				product_location=tracking_json[-1]['location'].encode('ascii','ignore')
				print len(tracking_json)
				print "asd"
				raw_data=' '
				for x in range (0,len(tracking_json)):
					raw_data=raw_data+ tracking_json[-1]['status'].encode('ascii','ignore') +"&nbsp; &nbsp;"+ tracking_json[-1]['date'].encode('ascii','ignore')+"&nbsp; &nbsp;"+ tracking_json[-1]['location'].encode('ascii','ignore')+"<br>"
				
				print raw_data
				print '3.5'
				l.append({"product_name":product_name,"product_quantity":product_quantity,"product_weight":product_weight,"product_applied_weight":product_applied_weight,"product_price":product_price,"product_shipping_cost":product_shipping_cost,"product_status":raw_data,"product_date":product_date,"product_location":product_location,"product_sku":product_sku,"product_trackingid":product_trackingid,})
				print '4'
			data= json.dumps(l)

			#bundle.data['products']=data
			bundle.data['products']=l
			
			bundle.data['status']=order.status
			bundle.data['date']=order.book_time.date()
			# bundle.data['time']=order.book_time.time()
			
			# bundle.data['order_no']=436+int(bundle.data['id'])
			# print bundle.data['order_no']
		except:
			print "shit"

		#bundle.data['ucts']=[{"product_date": "2015-06-07 18:40:20 ", "product_price": 50, "product_location": "Mumbai (Maharashtra)", "product_applied_weight": "null", "product_method": "Premium", "product_quantity": "null", "product_status": "Booking Received", "product_name": "clothes", "product_weight": 2, "product_shipping_cost": "null"}, {"product_date": "2015-06-07 18:40:20 ", "product_price": 60, "product_location": "Mumbai (Maharashtra)", "product_applied_weight": "null", "product_method": "Bulk", "product_quantity": "null", "product_status": "Booking Received", "product_name": "books", "product_weight": 7, "product_shipping_cost": "null"}]

		return bundle


class ProductResource(CORSModelResource):
	order = fields.ForeignKey(OrderResource, 'order' ,null=True)
	class Meta:
		queryset = Product.objects.all()
		resource_name = 'product'
		authorization= Authorization()
		always_return_data = True
		ordering = ['date']

	def build_filters(self, filters=None):
		print "shit"
		print filters
		if filters is None:
			filters = {}
		orm_filters = super(ProductResource, self).build_filters(filters)

		if 'q' in filters:
			orm_filters['q'] = filters['q']
		return orm_filters

	def apply_filters(self, request, orm_filters):
		base_object_list = super(ProductResource, self).apply_filters(request, {})
		print orm_filters
		if 'q' in orm_filters:
			return base_object_list.filter(order__business__username=orm_filters['q'])
		print base_object_list
		return base_object_list
	
	def hydrate(self,bundle):
		try:
			override_method=bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
			print "changed to PATCH"
		except:
			override_method='none'
			print "hello"

		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method!='PATCH':
			print "hhhhhhhhhhhh"
			try:
				business=Business.objects.get(pk=bundle.data['username'])
				bundle.data['business']="/bapi/v1/business/"+str(bundle.data['username'])+"/"
				print "user identified"
			except:
				#print "fuck"
				bundle.data['business']="/bapi/v1/business/0/"
				bundle.data["msg"]='notregistered'
				print "user not identified"
				return bundle

			#create order
	#curl --dump-header - -H "Content-Type: application/json" -X POST --data '{ "username": "newuser3", "name": "asd" , "phone":"8879006197","street_address":"office no 307, powai plaza","city":"mumbai","state":"maharashtra" ,"pincode":"400076","country":"india" , "payment_method":"F" ,"pname":"['clothes','books']","pprice":"['50','60']" ,"pweight":"['2','7']" }' http://127.0.0.1:8000/bapi/v1/order/		
			try:
				order =Order.objects.create(business=business,name=bundle.data['name'],phone=bundle.data['phone'],address1=bundle.data['address1'],address2=bundle.data['address2'],city=bundle.data['city'],state=bundle.data['state'],pincode=bundle.data['pincode'],country=bundle.data['country'],payment_method=bundle.data['payment_method'],reference_id=bundle.data['reference_id'],email=bundle.data['email'],method=bundle.data['method'])
				print "order created	"

				print "check here"				
				print isinstance(bundle.data['pname'], list)
				print "check here"
				
				if (isinstance(bundle.data['pname'], list)):
					try:
						#print bundle.data['array'][0]
						#print len(bundle.data['array'])

						for x in range (0,len(bundle.data['pname'])-1):
							product =Product.objects.create(order=order,name=bundle.data['pname'][x],weight=bundle.data['pweight'][x],price=bundle.data['pprice'][x],sku=bundle.data['psku'][x],quantity=bundle.data['pquantity'][x])
					except:
						bundle.data['errormsg']='error creating product'
			except Exception,e:
				print str(e)
				print "error"
				bundle.data['errormsg']='error creating order'

			if (isinstance(bundle.data['pname'], list)):	
				x=x+1
				bundle.data['name']=str(bundle.data['pname'][x])
				bundle.data['weight']=str(bundle.data['pweight'][x])
				bundle.data['price']=str(bundle.data['pprice'][x])
	#			bundle.data['method']=str(bundle.data['pmethod'][x])
				bundle.data['sku']=str(bundle.data['psku'][x])
				bundle.data['quantity']=str(bundle.data['pquantity'][x])
			else:
				bundle.data['name']=str(bundle.data['pname'])
				bundle.data['weight']=str(bundle.data['pweight'])
				bundle.data['price']=str(bundle.data['pprice'])
	#			bundle.data['method']=str(bundle.data['pmethod'])
				bundle.data['sku']=str(bundle.data['psku'])
				bundle.data['quantity']=str(bundle.data['pquantity'])



			bundle.data['order']="/bapi/v1/order/"+ str(order.pk) + "/"

			return bundle


		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method=='PATCH':
			print "patch"
			return bundle

	def obj_delete(self, bundle, **kwargs):
		#print bundle.data['id']
		pk=bundle.request.path.split('/')[4]
		product=Product.objects.get(pk=pk)
		status=product.order.status
		if status=='P': # validated
			bundle.data["delete"]="True"
			super(ProductResource, self).obj_delete(bundle, **kwargs)
		else:
		# TODO
		# do my thing here
			bundle.data["delete"]="False"
			pass



	def dehydrate(self,bundle):

		
		try:
			pk=bundle.data['order'].split('/')[4]
			order=Order.objects.get(pk=pk)
			bundle.data['recipient_name']=order.name
			bundle.data['city']=order.city
			bundle.data['status']=order.status
			bundle.data['date']=order.book_time.date()
			bundle.data['time']=order.book_time.time()
			
			bundle.data['order_no']=436+int(bundle.data['id'])
			print bundle.data['order_no']
		except:
			print "shit"
		return bundle


class XResource(CORSModelResource):
	class Meta:
		queryset = X.objects.all()
		resource_name = 'x'
		authorization= Authorization()
		always_return_data = True


class PricingResource(CORSModelResource):
	business = fields.ForeignKey(BusinessResource, 'business' ,null=True)
	class Meta:
		queryset = Pricing.objects.all()
		resource_name = 'pricing'
		authorization= Authorization()
		always_return_data = True

	def build_filters(self, filters=None):
		print "shit"
		print filters
		if filters is None:
			filters = {}
		orm_filters = super(PricingResource, self).build_filters(filters)

		if 'q' in filters:
			orm_filters['q'] = filters['q']
		return orm_filters

	def apply_filters(self, request, orm_filters):
		base_object_list = super(PricingResource, self).apply_filters(request, {})
		print orm_filters
		if 'q' in orm_filters:
			return base_object_list.filter(business__username=orm_filters['q'])
		print base_object_list
		return base_object_list

	def dehydrate(self,bundle):

		bundle.data['city']="asd"
		return bundle



class ForgotpassResource(CORSModelResource):
	business = fields.ForeignKey(BusinessResource, 'business' ,null=True)
	class Meta:
		queryset = Forgotpass.objects.all()
		resource_name = 'forgotpass'
		authorization= Authorization()
		excludes = ['auth']
		always_return_data = True

	def hydrate(self,bundle):
		try:
			business=Business.objects.get(pk=bundle.data['username'])
			bundle.data['business']="/bapi/v1/business/"+str(bundle.data['username'])+"/"
			print "user identified"
		except:
				#print "fuck"
			bundle.data['business']="/bapi/v1/business/0/"
			bundle.data["msg"]='notregistered'
			print "user not identified"
			return bundle

		bundle.data['auth']=hashlib.sha224( str(random.getrandbits(256))).hexdigest();
		email=business.email
		mail="www.sendd.co/?auth="+bundle.data['auth']+"&username="+bundle.data['username']
		subject="Reset password with sendd."
		send_mail(subject, mail, "Team Sendd <sargun@sendd.co>", [email])
		bundle.data["msg"]='success'
		return bundle



class ChangepassResource(CORSModelResource):
	business = fields.ForeignKey(BusinessResource, 'business' ,null=True)
	class Meta:
		queryset = Changepass.objects.all()
		resource_name = 'changepass'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			business=Business.objects.get(pk=bundle.data['username'])
			bundle.data['business']="/bapi/v1/business/"+str(bundle.data['username'])+"/"
			print "user identified"
		except:
				#print "fuck"
			bundle.data['business']="/bapi/v1/business/0/"
			bundle.data["msg"]='notregistered'
			print "user not identified"
			return bundle

		try:
			auth=bundle.data['auth']
			forgotpass=Forgotpass.objects.filter(business=business,auth=auth)
			if (forgotpass.count()==0) :
				bundle.data["msg"]="wrongauth"
				bundle.data["changed"]="N"
			else:
				print "kjkjkjkj"
				business.password=bundle.data['password']
				business.save()
				bundle.data["msg"]="password changed"
				bundle.data["changed"]="Y"
		except:
			if (business.password==bundle.data['old_password']):
				business.password=bundle.data['new_password']
				business.save()
				bundle.data["msg"]="password changed"
				bundle.data["changed"]="Y"

			else:
				bundle.data["msg"]="wrong password"
				bundle.data["changed"]="N"

		return bundle




'''
class UserResource2(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		authorization= Authorization()
		always_return_data = True
	def hydrate(self, bundle):
		print bundle.request
		try:
			override_method=bundle.request.META['HTTP_X_HTTP_METHOD_OVERRIDE']
			print "changed to PATCH"
		except:
			override_method='none'
			print "hello"

		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method!='PATCH':
			print "went in"
			try:
				if (bundle.data['web']=="Y"):
					pass
					

			except: 
				try:
					user=User.objects.get(pk=bundle.data['phone'])
					print "fuck"
					#undle.data['phone']=0
					bundle.data["msg"]='olduser'
					bundle.data['otp'] = randint(1000, 9999)
					msg0="http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
					msga=str(bundle.data['phone'])
					msg1="&msg=Welcome+to+Sendd.+Your+OTP+is+"
					msg2=str(bundle.data['otp'])
					msg3=".This+message+is+for+automated+verification+purpose.+No+action+required.&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&v=1.1&format=text"
					#url1="http://49.50.69.90//api/smsapi.aspx?username=doormint&password=naman123&to="+ str(bundle.data['phone']) +"&from=DORMNT&message="
					query=''.join([msg0,msga,msg1,msg2,msg3])
					print query
					x=urllib2.urlopen(query).read()
					print x
					print "hjhjhjhj"

					try:
						gcmdevice=GCMDevice.objects.filter(registration_id=bundle.data['gcmid'])
						if (gcmdevice.count()==0) :
							gcmdevice = GCMDevice.objects.create(registration_id=bundle.data['gcmid'])
						else:
							print "GCM device already exist"
							
					except:
						print "GCM device not created"
					
				except:
					print "shit"
					bundle.data["msg"]='newuser'	
					bundle.data['otp'] = randint(1000, 9999)
					msg0="http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
					msga=str(bundle.data['phone'])
					msg1="&msg=Welcome+to+Sendd.+Your+OTP+is+"
					msg2=str(bundle.data['otp'])
					msg3=".This+message+is+for+automated+verification+purpose.+No+action+required.&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&v=1.1&format=text"
					#url1="http://49.50.69.90//api/smsapi.aspx?username=doormint&password=naman123&to="+ str(bundle.data['phone']) +"&from=DORMNT&message="
					query=''.join([msg0,msga,msg1,msg2,msg3])
					print query
					urllib2.urlopen(query).read()
					#mail="Dear "+str(bundle.data['name'])+",\n\nWe are excited to have you join us and start shipping in a hassle free and convenient manner.\n\nOur team is always there to ensure that you have the best possible experience with us. Some of the questions that are frequently asked can be seen on the website as well as the app.\n\nIf you have any other query, you can get in touch with us at +91-8080028081 or mail us at help@sendd.co\n\n\nRegards,\nTeam Sendd"
					#subject=str(bundle.data["name"])+", Thanks for signing up with sendd."
					#send_mail(subject, mail, "Team Sendd <hello@sendd.co>", [str(bundle.data["email"])])

					try:
						gcmdevice=GCMDevice.objects.filter(registration_id=bundle.data['gcmid'])
						if (gcmdevice.count()==0) :
							gcmdevice = GCMDevice.objects.create(registration_id=bundle.data['gcmid'])
						else:
							print "GCM device already exist"
							
					except:
						print "GCM device not created"



			return bundle
		if bundle.request.META['REQUEST_METHOD'] == 'PUT':
			print "dfjfsdkjfdskj"
			queryset= User.objects.get(phone=bundle.data['phone'])
			print bundle.data['otp1']
			print queryset.otp

			if (str(bundle.data['otp1'])==str(queryset.otp)):
			 #generate apikey if otp recieved = otp sent
				bundle.data['apikey']=hashlib.sha224( str(random.getrandbits(256)) ).hexdigest();
				print bundle.data['apikey']
				bundle.data['valid']=1
			else:
				#bundle.data['otp'].del()
				print "nahi hua"
				bundle.data['valid']=0
			return bundle

		if bundle.request.META['REQUEST_METHOD'] == 'POST' and override_method=='PATCH':
			print "patch"
			try:
				gcmdevice=GCMDevice.objects.filter(registration_id=bundle.data['gcmid'])
				if (gcmdevice.count()==0) :
					gcmdevice = GCMDevice.objects.create(registration_id=bundle.data['gcmid'])
				else:
					print "GCM device already exist"
					
			except:
				print "GCM device not created"


			return bundle


class AddressResource2(MultipartResource,ModelResource):
	class Meta:
		queryset = Address.objects.all()
		resource_name = 'address'
		authorization= Authorization()
		always_return_data = True


class NamemailResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user')
	class Meta:
		queryset = Namemail.objects.all()
		resource_name = 'namemail'
		authorization= Authorization()
		always_return_data = True


class WeborderResource2(MultipartResource,ModelResource):
	class Meta:
		queryset = Weborder.objects.all()
		resource_name = 'weborder'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self, bundle):
		
		#creating user if doesnt exist
		try:
			newuser=User.objects.get(pk=bundle.data['number'])
		except:
			newuser= User.objects.create(phone=bundle.data['number'])
			#newuser.save()
			pk=newuser.pk

			
		
		#create nameemail
		try:
			newnamemail=Namemail.objects.filter(user=newuser,name=bundle.data['name'],email=bundle.data['email'])
			if (newnamemail.count()==0) :
				newnamemail = Namemail.objects.create(user=newuser,name=bundle.data['name'],email=bundle.data['email'])
				newnamemail.save()
				pk=newnamemail.pk
			#bundle.obj = Address(address="nick", locality = "", password,timezone.now(),"od_test")
			else :
				for x in newnamemail:
					pk= x.id

		except:
			print "cool shit"
		

		#create order
		try:
			neworder=Order.objects.create(namemail=newnamemail,user=newuser,address=bundle.data['pickup_location'],way='W',pick_now='N',pincode=bundle.data['pincode'])
		#neworder.save()
			order_pk=neworder.pk
		except:
			print "cool shit"
		
		#create address
		try:
			address=Address.objects.create()
		except:
			print "haw"


		#create shipment
		try:
			shipment=Shipment.objects.create(order=neworder,item_name=bundle.data['item_details'],drop_address=address)
		except:
			print "haw"


		try:	
			mail="Dear "+str(bundle.data["name"]) +",\n\nWe have successfully received your booking.\n\nYou will shortly receive details of the pick up representative who will come to collect your parcel at your designated time.\n\nIf you have any query, you can get in touch with us at +91-8080028081 or mail us at help@sendd.co\n\n\nRegards,\nTeam Sendd"
			subject=str(bundle.data["name"]) + ", We have received your parcel booking."
			send_mail(subject, mail, "Team Sendd <hello@sendd.co>", [str(bundle.data["email"]),"Team Sendd <hello@sendd.co>"])
		except:
			print "mail not sent"
		
		return bundle


class ForgotpassResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user')
	class Meta:
		queryset = Forgotpass.objects.all()
		resource_name = 'forgotpass'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			user=User.objects.get(pk=bundle.data['phone'])
			bundle.data['user']="/api/v2/user/"+str(bundle.data['phone'])+"/"
			bundle.data['msg']="user exists"
			bundle.data['auth']=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))
		
		except:
			bundle.data['user']="/api/v2/user/0/"	
			bundle.data['msg']="user not exist"

		return bundle

	def dehydrate(self,bundle):
		bundle.data['auth']="GEN"
		return bundle

class PromocodeResource2(MultipartResource,ModelResource):
	#user = fields.ForeignKey(UserResource2, 'user' ,null=True)
	class Meta:
		queryset = Promocode.objects.all()
		resource_name = 'promocode'
		authorization= Authorization()
		always_return_data = True


class OrderResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user')
	namemail = fields.ForeignKey(NamemailResource2, 'namemail',null=True,blank=True)
	promocode = fields.ForeignKey(PromocodeResource2, 'promocode',null=True,blank=True)
	
	class Meta:
		queryset = Order.objects.all()
		resource_name = 'order'
		authorization= Authorization()
		always_return_data = True
		filtering = {
			"user": ALL,
		}

	def hydrate(self,bundle):
		pk=int(bundle.data['user'])
		
		bundle.data['user']="/api/v2/user/"+str(bundle.data['user'])+"/"
		print bundle.data['user']
		cust=User.objects.get(pk=pk)

		#promocode

		try:
			promocode=Promocode.objects.get(pk=bundle.data['code'])

			print '1'
			
			if (promocode.only_for_first=='Y'):
				shipment=Shipment.objects.filter(order__user__phone=bundle.data['phone'])
				if (shipment.count()==0):
					#everything good
					bundle.data['promocode']="/api/v2/promocode/"+str(promocode.pk)+"/"
					print str(bundle.data['code'])
					bundle.data['valid']='Y'
				else:
					bundle.data['promomsg']="You are not a first time user"
					#bundle.data['valid']='N'
			else:
				bundle.data['promocode']="/api/v2/promocode/"+str(promocode.pk)+"/"
				print str(bundle.data['code'])
				#bundle.data['valid']='Y'
		except:
			bundle.data['promomsg']="Wrong promo code"
			#bundle.data['valid']='N'
			print '2'
		#print bundle.data['promocode']

		#create nameemail
		try:
			newnamemail=Namemail.objects.filter(user=cust,name=bundle.data['name'],email=bundle.data['email'])
			if (newnamemail.count()==0) :
				newnamemail = Namemail.objects.create(user=cust,name=bundle.data['name'],email=bundle.data['email'])
				newnamemail.save()
				nm_pk=newnamemail.pk
			#bundle.obj = Address(address="nick", locality = "", password,timezone.now(),"od_test")
			else :
				for x in newnamemail:
					nm_pk= x.pk
			bundle.data['namemail']="/api/v2/namemail/"+str(nm_pk)+"/"
		
		except:
			print "cool shit"

		
		return bundle


class ShipmentResource2(MultipartResource,ModelResource):
	order=fields.ForeignKey(OrderResource2, 'order', null=True, blank=True)
	drop_address= fields.ForeignKey(AddressResource2, 'drop_address', null=True, blank=True)
	img = fields.FileField(attribute="img", null=True, blank=True)
	class Meta:
		queryset = Shipment.objects.all()
		resource_name = 'shipment'
		detail_uri_name = 'real_tracking_no'
		authorization= Authorization()
		always_return_data = True
		filtering = {
			"drop_address": ALL,
		}

	def prepend_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/(?P<real_tracking_no>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
		]



	#def over_urls(self):
	#	return [
	#   	url(r'^(?P<resource_name>%s)/(?P<track>[\w\.-]+)/$' % self._meta.resource_name, self.wrap_view('dispatch_detail'), name='api_dispatch_detail_track'),
	#        ]

	def build_filters(self, filters=None):
		print "shit"
		print filters
		if filters is None:
			filters = {}
		orm_filters = super(ShipmentResource2, self).build_filters(filters)

		if 'q' in filters:
			orm_filters['q'] = filters['q']
		return orm_filters

	def apply_filters(self, request, orm_filters):
		base_object_list = super(ShipmentResource2, self).apply_filters(request, {})
		print orm_filters
		if 'q' in orm_filters:
			return base_object_list.filter(order__user__phone=orm_filters['q'])
		print base_object_list
		return base_object_list

	def hydrate(self,bundle):



#sending mail and sms
		try:
			order=Order.objects.get(pk=bundle.data['order'])
			email= order.namemail.email
			name= order.namemail.name
			phone= order.user.phone

			

			
			msg0="http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
			msga=urllib.quote(str(phone))
			msg1="&msg=Hi+"
			msg2=urllib.quote(str(name))
			msg3="%2C+your+booking+for+parcel+has+been+received.+You+will+shortly+receive+the+contact+of+our+authorized+pickup+boy+and+a+call+on+"
			#url1="http://49.50.69.90//api/smsapi.aspx?username=doormint&password=naman123&to="+ str(bundle.data['phone']) +"&from=DORMNT&message="
			msg4=urllib.quote(str(phone))
			msg5="+for+details.&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&v=1.1&format=text"
			query=''.join([msg0,msga,msg1,msg2,msg3,msg4,msg5])
			print query
			#bundle.data['query']=query
			urllib2.urlopen(query)
			try:	
				mail="Dear "+str(name) +",\n\nWe have successfully received your booking.\n\nYou will shortly receive details of the pick up representative who will come to collect your parcel at your designated time.\n\nIf you have any query, you can get in touch with us at +91-8080028081 or mail us at help@sendd.co\n\n\nRegards,\nTeam Sendd"
				subject=str(name) + ", We have received your parcel booking."
				send_mail(subject, mail, "Team Sendd <hello@sendd.co>", [str(email),"Team Sendd <hello@sendd.co>"])
			except:
				print "mail not sent"	



		except:
			print "error"

#
		try:
			bundle.data['order']="/api/v2/order/"+str(bundle.data['order'])+"/"
		except:
			print "sd"

		try:
			address_on_database=Address.objects.filter(flat_no=bundle.data['drop_flat_no'],locality=bundle.data['drop_locality'],city=bundle.data['drop_city'],state=bundle.data['drop_state'],country=bundle.data['drop_country'],pincode=bundle.data['drop_pincode'])


			if (address_on_database.count()==0) :
				address_on_database = Address.objects.create(flat_no=bundle.data['drop_flat_no'],locality=bundle.data['drop_locality'],city=bundle.data['drop_city'],state=bundle.data['drop_state'],country=bundle.data['drop_country'],pincode=bundle.data['drop_pincode'])
				address_on_database.save()
				pk=address_on_database.pk
			#bundle.obj = Address(address="nick", locality = "", password,timezone.now(),"od_test")
			else :
				for x in address_on_database:
					pk= x.id
			#queryset= Address.objects.get(number=bundle.data['number'])
			bundle.data['drop_address']="/api/v2/address/"+str(pk)+"/"

		except:
			print "fu"

		return bundle

	def dehydrate(self,bundle):
		try:
			print 'dfd'
			print bundle.data['drop_address']
			pk=bundle.data['drop_address'].split('/')[4]
			print pk
			address=Address.objects.get(pk=pk)
			bundle.data['drop_address']=address
			print address
			bundle.data['pincode']=address.pincode

		except:
			print "df"

		try:
			bundle.data['img']='http://128.199.159.90/static'+str(bundle.data['img'])[15:]
		except:
			print 'img'


		try:
			order_pk=pk=bundle.data['order'].split('/')[4]
			order=Order.objects.get(pk=pk)
			bundle.data['date']=order.date
			bundle.data['time']=order.time
			bundle.data['address']=order.address

			bundle.data['name']=order.name
			bundle.data['email']=order.email
			user=order.user
			bundle.data['name']=order.name
			bundle.data['phone']=user.phone
			bundle.data['order']=bundle.data['order'].split('/')[4]	


		except:
			print "sad"

		try:
			bundle.data['tracking_no'],bundle.data['real_tracking_no']=bundle.data['real_tracking_no'],bundle.data['tracking_no']
		except:
			'tracking number failed'
		return bundle


class XResource2(MultipartResource,ModelResource):
	C = fields.FileField(attribute="C", null=True, blank=True)
	order=fields.ForeignKey(OrderResource2, 'order' , null=True , blank =True)
	class Meta:
		queryset = X.objects.all()
		resource_name = 'x'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self, bundle):



		# print bundle.request
		#print bundle.data['Name']
		bundle.data['Cd']='dsds'
		return bundle



class PriceappResource2(MultipartResource,ModelResource):
	class Meta:
		queryset = Priceapp.objects.all()
		resource_name = 'priceapp'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self, bundle):
		premium=[(60,30),(90,45),(120,50),(140,60),(160,65)]
		standard=[(30,28),(60,42),(80,47),(100,57),(105,62)]
		economy=[(240,15,30),(260,15,32),(280,15,34),(290,15,35),(290,15,35)]

		zone=3
		pin=bundle.data['pincode']
		if(pin.isdigit()):
			#getting zone

			t=pin[:2]
			z=pin[:3]
			bundle.data['zone']=zone

			if (t=='40' and z!= '403'):
				zone=0
				bundle.data['zone']=zone

			if (t=='41' or t=='42' or t=='43' or t=='44'):
				zone=1
				bundle.data['zone']=zone

			if (t=='56' or t=='11' or t=='60' or t=='70'):
				zone=2
				bundle.data['zone']=zone

			if (t=='78' or t=='79' or t=='18' or t=='19'):
				zone=4
				bundle.data['zone']=zone


		else:
			pin=str(pin)
			pin=urllib.quote(pin)
			state= cities[pin]
			if 'Mumbai' in pin: 
				zone=0
			elif state=='Maharashtra':
				zone=1
			elif (('Chennai' in pin) or ('Delhi' in pin) or ('Kolkata' in pin) or ('Banglore' in pin) or ('Bangalore' in pin)):
				zone=2
			elif ((state=='Jammu and Kashmir') or (state=='Assam') or (state=='Arunachal Pradesh') or (state=='Manipur') or (state=='Meghalaya') or (state=='Mizoram') or (state=='Nagaland')or (state=='Tripura')):
				zone=4

			bundle.data['zone']=zone


		try:
			l=float(bundle.data['l'])
			b=float(bundle.data['b'])
			h=float(bundle.data['h'])
			vol=(l*b*h)/5000
		except:
			vol=0	

		w=float(bundle.data['weight'])

		if (vol>w):
			w=vol
		print w
		premiumprice=1*premium[zone][0]+ (math.ceil(2*w-1))*premium[zone][1]
		standardprice=1*standard[zone][0]+ (math.ceil(2*w-1))*standard[zone][1]
		if (w>=10):
			economyprice=economy[zone][0]+4*economy[zone][1]+math.ceil(w-10)*economy[zone][2]
		elif(w>=6):
			economyprice=economy[zone][0]+math.ceil(w-6)*economy[zone][1]
		else:
			economyprice='-'

		bundle.data['premium']=premiumprice
		bundle.data['standard']=standardprice
		bundle.data['economy']=economyprice
			
			#premium

			# print bundle.request
			#print bundle.data['Name']
		return bundle			


class DateappResource2(MultipartResource,ModelResource):
	class Meta:
		queryset = Dateapp.objects.all()
		resource_name = 'dateapp'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self, bundle):
		premium=[('1 Day'),('1-2 Days'),('1-2 Days'),('2-3 Days'),('2-3 Days')]
		standard=[('2 Days'),('2-3 Days'),('2-3 Days'),('3-4 Days'),('3-4 Days')]
		economy=[('2-3 Days'),('3-4 Days'),('5-6 Days'),('5-6 Days'),('7-8 Days')]
		pin=bundle.data['pincode']
		#getting zone
		zone=3
		pin=bundle.data['pincode']
		if(pin.isdigit()):
			#getting zone

			t=pin[:2]
			bundle.data['zone']=zone

			if (t=='40'):
				zone=0
				bundle.data['zone']=zone

			if (t=='41' or t=='42' or t=='43' or t=='44'):
				zone=1
				bundle.data['zone']=zone

			if (t=='56' or t=='11' or t=='60' or t=='70'):
				zone=2
				bundle.data['zone']=zone

			if (t=='78' or t=='79' or t=='18' or t=='19'):
				zone=4
				bundle.data['zone']=zone


		else:
			pin=str(pin)
			pin=urllib.quote(pin)
			state= cities[pin]
			if 'Mumbai' in pin: 
				zone=0
			elif state=='Maharashtra':
				zone=1
			elif (('Chennai' in pin) or ('Delhi' in pin) or ('Kolkata' in pin) or ('Banglore' in pin) or ('Bangalore' in pin)):
				zone=2
			elif ((state=='Jammu and Kashmir') or (state=='Assam') or (state=='Arunachal Pradesh') or (state=='Manipur') or (state=='Meghalaya') or (state=='Mizoram') or (state=='Nagaland')or (state=='Tripura')):
				zone=4

			bundle.data['zone']=zone



		premiumprice=premium[zone]
		standardprice=standard[zone]
		economyprice=economy[zone]
		bundle.data['premium']=premiumprice
		bundle.data['standard']=standardprice
		bundle.data['economy']=economyprice
		
		#premium

		# print bundle.request
		#print bundle.data['Name']
		return bundle


class LoginSessionResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user' ,null=True)
	class Meta:
		queryset = LoginSession.objects.all()
		resource_name = 'loginsession'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			user=User.objects.get(pk=bundle.data['phone'])
		except:
			print "fuck"
			bundle.data["success"]='notregistered'
			return bundle

		password=user.password
		bundle.data['user']="/api/v2/user/"+str(bundle.data['phone'])+"/"
		salt='crawLINGINmySKin'
		passw= str(bundle.data['password'])
		print passw
		hsh = hashlib.sha224(passw+salt).hexdigest()

		print user.name
		
		if (hsh== password):
			bundle.data["success"]='success'
			bundle.data['email']=user.email
			bundle.data['phone']=user.phone
			bundle.data['name']=user.name
			bundle.data['apikey']=user.apikey
		print bundle.data['user']
		print bundle.data['password']
		return bundle


class PromocheckResource2(MultipartResource,ModelResource):
	user = fields.ForeignKey(UserResource2, 'user' ,null=True)
	class Meta:
		queryset = Promocheck.objects.all()
		resource_name = 'promocheck'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):
		try:
			user=User.objects.get(pk=bundle.data['phone'])
			bundle.data['user']="/api/v2/user/"+str(bundle.data['phone'])+"/"
		except:
			bundle.data["promomsg"]='Please register first'
			return bundle

		try:
			promocode=Promocode.objects.get(pk=bundle.data['code'])
			
			if (promocode.only_for_first=='Y'):
				shipment=Shipment.objects.filter(order__user__phone=bundle.data['phone'])
				if (shipment.count()==0):
					#everything good
					bundle.data['promomsg']=promocode.msg
					bundle.data['valid']='Y'
				else:
					bundle.data['promomsg']="You are not a first time user"
					bundle.data['valid']='N'
			else:
				bundle.data['promomsg']=promocode.msg
				bundle.data['valid']='Y'
		except:
			bundle.data['promomsg']="Wrong promo code"
			bundle.data['valid']='N'
		return bundle

	




class PincodecheckResource2(MultipartResource,ModelResource):
	class Meta:
		queryset = Pincodecheck.objects.all()
		resource_name = 'pincodecheck'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):

		goodpincodes=['400076','400072','400078','400077','400080','400079']

		if bundle.data['pincode'] in goodpincodes:
			bundle.data['valid']=1
		else:
			bundle.data['valid']=0
			bundle.data['msg']='we dont have pickup service available in your desired pickup location.'

		return bundle
'''