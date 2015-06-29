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
        
        #these 2 lines due to product wanting to use this authorisation
        if (bundle.request.META["HTTP_AUTHORIZATION"]=='A'):
        	return True

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

        print "fgd"
        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            if obj.user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
    	print "dfd"
        return bundle.request.META["HTTP_AUTHORIZATION"]==bundle.obj.business.apikey


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
	#	excludes = ['password']
		authorization= Authorization()
		always_return_data = True

	def dehydrate(self,bundle):


		pk=bundle.data['resource_uri'].split('/')[4]

		try:
			business=Business.objects.get(pk=pk)
		except:
			print "fuck"
			bundle.data["msg"]='notregistered'
			return bundle


		#pk=bundle.data['resource_uri'].split('/')[4]

		try:
			u = User.objects.get(username=business.businessmanager.username)
			bundle.data['manager']=u.businessmanager.first_name 
			bundle.data['manager_number']=u.businessmanager.phone
		
		except:
			bundle.data['manager']='Ankush Sharma'
			bundle.data['manager_number']='8080772210'
			#u = User.objects.get(username='ankit')
			#print u.businessmanager.phone



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

		bundle.data["cost"]='N/A'
		bundle.data["paid"]='N/A'
		bundle.data["due"]='N/A'
				

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
		ordering = ['book_time']


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
					raw_data=raw_data+ tracking_json[x]['status'].encode('ascii','ignore') +"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"+ tracking_json[x]['date'].encode('ascii','ignore')+"&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;"+ tracking_json[x]['location'].encode('ascii','ignore')+"<br>"
				
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
		authorization=Authorization()
		authentication=Authentication()
		always_return_data = True
		ordering = ['date']

	def prepend_urls(self):
		return [
            url(r"^(?P<resource_name>%s)/(?P<real_tracking_no>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]


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

	


'''


class PincodecheckResource(CORSModelResource):
	class Meta:
		queryset = Pincodecheck.objects.all()
		resource_name = 'pincodecheck'
		authorization= Authorization()
		always_return_data = True

	def hydrate(self,bundle):

		goodpincodes=['110001','110002','110003','110004','110005','110006','110007','110008','110009','110010','110011','110012','110013','110014','110015','110016','110017','110018','110019','110020','110021','110022','110023','110024','110025','110026','110027','110028','110029','110030','110031','110032','110033','110034','110035','110036','110037','110038','110039','110040','110041','110042','110043','110044','110045','110046','110047','110048','110049','110050','110051','110052','110053','110054','110055','110056','110057','110058','110059','110060','110061','110062','110063','110064','110065','110066','110067','110068','110069','110070','110071','110072','110073','110074','110075','110076','110077','110078','110080','110081','110082','110083','110084','110085','110086','110087','110088','110089','110090','110091','110092','110093','110094','110095','110096','110101','110103','110104','110105','110106','110107','110108','110109','110110','110112','110113','110114','110115','110116','110117','110118','110119','110120','110122','110124','110125','110301','110302','110501','110502','110503','110504','110505','110510','110511','110512','110601','110602','110603','110604','110605','110606','110607','110608','110609','121000','121001','121002','121003','121004','121005','121006','121007','121008','121009','121101','121102','121106','121107','121206','122000','122001','122002','122003','122004','122005','122006','122007','122008','122009','122010','122011','122012','122013','122014','122015','122016','122017','122018','122050','122051','122100','122101','122102','122103','122105','122106','122109','123001','123003','123106','123401','123501','123507','124001','124003','124021','124103','124104','124112','124303','124413','124505','124507','124514','125001','125002','125003','125004','125005','125006','125011','125012','125021','125022','125033','125034','125044','125050','125051','125052','125053','125055','125056','125076','125111','125112','125201','126102','126103','126112','126113','126115','126116','126120','127020','127021','127028','127201','127306','131001','131021','131024','131027','131028','131029','131101','132000','132001','132022','132024','132027','132037','132041','132101','132102','132103','132104','132105','132106','132108','132110','132116','132117','132118','132119','132131','132135','132140','132151','132152','132153','133001','133004','133005','133006','133007','133104','133201','133302','134001','134002','134003','134004','134005','134006','134007','134101','134102','134107','134108','134109','134110','134111','134112','134113','134114','134115','134116','134118','135001','135002','135003','135004','136026','136027','136118','136119','136132','136135','140001','140101','140103','140105','140124','140301','140401','140412','140501','140504','140506','140507','140601','140603','141001','141002','141003','141004','141005','141006','141007','141008','141009','141010','141011','141012','141013','141014','141015','141016','141017','141020','141101','141102','141109','141112','141120','141301','141304','141309','141310','141400','141401','141421','142001','142021','142026','142027','142047','142050','143000','143001','143002','143003','143004','143005','143006','143007','143008','143009','143010','143021','143022','143026','143036','143101','143104','143105','143106','143401','143416','143501','143505','143506','143521','143531','144001','144002','144003','144004','144005','144006','144007','144008','144009','144010','144011','144012','144013','144014','144021','144022','144023','144027','144038','144102','144204','144205','144211','144401','144402','144409','144410','144505','144514','144601','144602','144801','145001','145101','146001','146002','146021','146022','146023','146024','147001','147002','147003','147004','147005','147021','147103','147201','147301','148000','148001','148021','148022','148023','148024','148025','148028','148100','148101','151001','151002','151003','151004','151005','151101','151103','151202','151203','151204','151301','151505','152001','152002','152024','152026','152101','152107','152116','160001','160002','160003','160004','160005','160006','160007','160008','160009','160010','160011','160012','160013','160014','160015','160016','160017','160018','160019','160020','160021','160022','160023','160024','160025','160026','160027','160028','160029','160030','160031','160032','160033','160034','160035','160036','160037','160038','160039','160040','160041','160042','160043','160044','160045','160046','160047','160048','160049','160050','160051','160052','160053','160054','160055','160056','160057','160058','160059','160060','160061','160062','160071','160101','160102','160103','160106','166031','171001','171002','171003','171004','171005','171006','171007','171008','171009','171010','171011','171012','172001','173001','173002','173025','173030','173033','173200','173201','173202','173204','173205','173209','173211','173212','173213','173220','174001','174101','174103','174303','174315','174401','174402','175000','175001','175002','175021','175023','175027','175101','175125','175131','176001','176002','176031','176047','176057','176061','176062','176201','176215','176216','176219','176402','176403','177001','177005','180001','180002','180003','180004','180005','180006','180007','180008','180009','180010','180011','180012','180013','180014','180015','180016','181101','181104','181121','181123','181124','181133','181152','181205','181206','182101','182220','184101','184102','184121','190001','190002','190003','190004','190005','190006','190007','190008','190009','190010','190011','190012','190013','190014','190015','190016','190017','190018','190019','190020','190021','190023','191101','191111','191201','192100','192101','192102','192122','192301','193100','193101','193102','193103','193201','201001','201002','201003','201004','201005','201006','201007','201008','201009','201010','201011','201012','201013','201014','201102','201201','201202','201204','201206','201300','201301','201302','201303','201304','201305','201306','201307','201308','201309','201310','201311','202001','202002','202410','202412','202525','202526','203001','203131','203132','203205','203207','204101','204214','204215','205001','205135','205151','206001','206002','206122','206241','206242','206244','206247','207001','207032','207123','207441','208001','208002','208003','208004','208005','208006','208007','208008','208009','208010','208011','208012','208013','208014','208015','208016','208017','208018','208019','208020','208021','208022','208023','208024','208025','208026','208027','209025','209101','209111','209201','209202','209311','209601','209625','209722','209724','209725','209726','209727','209801','209861','209862','210000','210001','210002','210003','210005','210006','210007','210008','210009','210010','210011','210012','210204','210301','210427','210431','211001','211002','211003','211004','211005','211006','211007','211008','211009','211010','211011','211012','211013','211014','211015','211016','211017','211018','211019','212061','212105','212207','212212','212402','212403','212404','212601','212621','221001','221002','221003','221004','221005','221006','221007','221008','221009','221010','221011','221102','221103','221104','221105','221106','221108','221109','221112','221145','221210','221301','221303','221304','221306','221307','221310','221311','221314','221401','221402','221409','221501','221503','221504','221506','221507','221712','221715','222001','222002','222202','224001','224122','224123','224137','224141','224190','224229','224235','224401','224509','225001','225003','225123','225401','225411','225414','226000','226001','226002','226003','226004','226005','226006','226007','226008','226009','226010','226011','226012','226013','226014','226015','226016','226017','226018','226019','226020','226021','226022','226023','226024','226025','226026','226028','226101','226102','226201','226301','226302','226303','226401','226501','227101','227105','227106','227305','227405','227409','227412','227809','227813','227817','228001','228118','229001','229006','229010','229206','229302','229404','229406','230001','230002','230003','230004','230005','230135','230153','230204','230205','230206','230207','230216','230219','230304','231001','231002','231205','231206','231207','231208','231210','231217','231218','231219','231220','231221','231222','231223','231225','231307','232101','232104','232108','232110','233001','241001','242001','242301','242306','242406','242407','243001','243002','243003','243004','243005','243006','243122','243123','243124','243201','243301','243400','243501','243502','243503','243601','243639','244001','244103','244221','244223','244235','244241','244302','244303','244443','244713','244715','244901','244921','245101','245207','245304','246001','246149','246171','246174','246401','246425','246429','246443','246444','246449','246455','246472','246701','246761','246924','247001','247002','247231','247232','247323','247325','247341','247554','247656','247661','247662','247663','247664','247666','247667','247668','247669','247776','248001','248002','248003','248004','248005','248006','248007','248008','248009','248010','248102','248110','248115','248116','248121','248125','248126','248140','248141','248142','248146','248160','248161','248165','248171','248179','248191','248195','248197','248198','248201','249001','249145','249161','249175','249192','249193','249199','249201','249202','249203','249204','249205','249302','249304','249401','249402','249403','249404','249405','249407','249408','249409','249410','249411','250001','250002','250003','250004','250005','250010','250013','250102','250103','250105','250110','250221','250342','250401','250402','250403','250609','250611','251001','251002','251003','251201','261001','261121','261201','261231','262001','262401','262402','262405','262701','262802','262902','263001','263002','263126','263136','263139','263140','263141','263145','263148','263153','263154','263601','263620','263623','263624','263625','263627','263636','263637','263639','263643','263668','263669','263670','263678','271001','271002','271201','271208','271302','271308','271313','271801','271831','271865','272001','272002','272003','272105','272131','272175','272189','272203','273001','273002','273003','273004','273005','273006','273007','273008','273009','273010','273012','273013','273014','273015','273164','273201','273202','273209','273303','273402','273412','274001','274201','274203','274301','274304','274401','274402','274406','274407','274509','275101','275304','275305','276001','277001','281001','281002','281003','281004','281005','281006','281121','281306','281401','281403','282001','282002','282003','282004','282005','282006','282007','282008','282009','282010','283110','283125','283201','283202','283203','283204','284001','284002','284003','284121','284128','284129','284135','284301','284305','284401','284402','284403','285001','285123','285204','285205','290725','301001','301017','301019','301020','301027','301030','301404','301405','301701','301705','301706','301707','302001','302002','302003','302004','302005','302006','302007','302008','302009','302010','302011','302012','302013','302014','302015','302016','302017','302018','302019','302020','302021','302022','302023','302025','302026','302028','302029','302033','302034','303001','303007','303101','303108','303303','303313','303327','303503','303702','303802','303902','304022','304023','304042','305001','305002','305003','305004','305005','305006','305007','305008','305009','305022','305023','305024','305404','305601','305624','305801','305802','305814','305816','305901','306001','306104','306115','306116','306302','306304','306401','306902','307026','307027','307501','307510','307526','311001','311011','311020','311021','311025','312001','312021','312601','313001','313002','313003','313004','313011','313015','313022','313023','313024','313031','313203','313205','313301','313324','313326','313603','313604','313802','313803','313901','314001','314025','314403','321001','321608','322001','322021','322201','322230','323001','323303','323305','323307','323603','324001','324002','324003','324004','324005','324006','324007','324008','324009','324010','325202','325205','325220','326001','326023','326502','326519','327001','328001','329090','331001','331021','331022','331023','331027','331029','331302','331303','331304','331403','331411','331501','331502','331507','331517','331801','331802','331803','331811','332001','332301','332311','333001','333025','333026','333029','333031','333042','333333','334001','334002','334003','334004','334005','334006','334021','334022','334023','334201','334202','334302','334305','334401','334402','334403','334601','334603','334604','334801','334803','334804','335001','335002','335022','335023','335027','335041','335051','335063','335073','335504','335512','335513','335526','335707','335802','335803','335804','341001','341021','341024','341025','341029','341301','341501','341502','341505','341508','341509','341510','341511','341512','342001','342002','342003','342004','342005','342006','342007','342008','342009','342010','342011','342012','342014','342015','342016','342024','342026','342301','342304','342601','342602','342604','342804','342902','343001','343029','343041','344001','344022','345001','345021','346002','346003','346004','346005','346050','346110','346240','360001','360002','360003','360004','360005','360006','360007','360008','360009','360021','360024','360026','360035','360311','360370','360375','360410','360510','360530','360560','360575','360576','360577','360578','360579','361001','361002','361003','361004','361005','361006','361007','361008','361009','361010','361110','361120','361140','361160','361170','361210','361305','361335','361345','361350','362001','362002','362003','362004','362220','362225','362265','362266','362267','362268','362269','362560','363001','363002','363020','363030','363035','363310','363610','363621','363641','363642','364001','364002','364003','364004','364005','364006','364240','364270','364290','364710','365560','365601','370001','370110','370140','370201','370202','370203','370205','370210','370230','370421','370465','370615','380001','380002','380003','380004','380005','380006','380007','380008','380009','380010','380012','380013','380014','380015','380016','380017','380018','380019','380021','380022','380023','380024','380025','380026','380027','380028','380050','380051','380052','380053','380054','380055','380057','380058','380059','380060','380061','380063','380152','382000','382001','382002','382003','382004','382005','382006','382007','382008','382009','382010','382011','382012','382013','382014','382015','382016','382017','382018','382019','382020','382021','382022','382023','382024','382025','382026','382027','382028','382029','382030','382041','382042','382044','382051','382110','382120','382150','382170','382210','382211','382213','382220','382315','382325','382330','382340','382345','382346','382350','382352','382405','382410','382415','382418','382420','382421','382422','382424','382427','382428','382430','382440','382442','382443','382445','382449','382470','382475','382480','382481','382655','382715','382721','382725','382729','382740','383001','383235','383255','383341','383430','384001','384002','384003','384011','384120','384151','384160','384170','384205','384206','384212','384246','384265','384310','384315','384410','384435','385001','385520','385535','387001','387002','387130','387220','387240','387315','387320','387345','387355','387370','387380','387540','387620','387810','388001','388110','388120','388121','388130','388205','388220','388305','388306','388307','388310','388315','388320','388325','388330','388335','388340','388345','388350','388355','388360','388370','388430','388440','388450','388470','388540','388545','388560','388620','389001','389140','389151','389230','389260','389330','389350','389351','389380','390001','390002','390003','390004','390005','390006','390007','390008','390009','390010','390011','390012','390013','390014','390015','390016','390017','390018','390019','390020','390021','390022','390023','390024','390025','391101','391240','391243','391310','391320','391330','391340','391345','391346','391347','391350','391410','391440','391510','391520','391740','391742','391745','391750','391760','391770','391775','392001','392002','392011','392012','392015','392130','392150','392220','393001','393002','393010','393110','393115','393145','394107','394110','394116','394120','394190','394210','394220','394221','394230','394270','394305','394327','394510','394515','394516','394518','394601','394650','395001','395002','395003','395004','395005','395006','395007','395008','395009','395010','395011','395013','395017','395023','396001','396002','396007','396020','396035','396105','396107','396120','396125','396126','396155','396165','396170','396171','396180','396185','396191','396193','396194','396195','396196','396197','396200','396209','396210','396211','396220','396230','396236','396240','396321','396325','396421','396424','396427','396445','396460','396521','400001','400002','400003','400004','400005','400006','400007','400008','400009','400010','400011','400012','400013','400014','400015','400016','400017','400018','400019','400020','400021','400022','400023','400024','400025','400026','400027','400028','400029','400030','400031','400032','400033','400034','400035','400036','400037','400038','400039','400040','400041','400042','400043','400046','400048','400049','400050','400051','400052','400053','400054','400055','400056','400057','400058','400059','400060','400061','400062','400063','400064','400065','400066','400067','400068','400069','400070','400071','400072','400074','400075','400076','400077','400078','400079','400080','400081','400082','400083','400084','400085','400086','400087','400088','400089','400090','400091','400092','400093','400094','400095','400096','400097','400098','400099','400101','400102','400103','400104','400105','400218','400601','400602','400603','400604','400605','400606','400607','400608','400609','400610','400611','400612','400613','400614','400615','400700','400701','400702','400703','400704','400705','400706','400707','400708','400709','400710','400901','401101','401102','401103','401104','401105','401106','401107','401201','401202','401203','401204','401205','401207','401208','401209','401210','401301','401302','401303','401304','401305','401401','401402','401403','401404','401407','401501','401502','401503','401504','401506','401601','401602','401608','401616','401706','402104','402106','402107','402108','402109','402125','402201','402203','402207','402208','402209','402301','402302','402309','403001','403002','403003','403004','403005','403006','403101','403102','403103','403104','403105','403106','403107','403108','403109','403110','403112','403114','403115','403201','403202','403203','403204','403206','403210','403325','403401','403402','403403','403404','403405','403406','403407','403409','403410','403501','403502','403503','403504','403505','403506','403507','403508','403509','403510','403511','403512','403513','403514','403515','403516','403517','403518','403519','403521','403523','403524','403526','403527','403529','403530','403531','403601','403602','403604','403701','403702','403703','403704','403705','403706','403707','403708','403709','403710','403711','403712','403713','403714','403715','403716','403717','403718','403719','403720','403721','403722','403723','403724','403725','403726','403727','403729','403731','403801','403802','403803','403804','403806','403808','407001','410200','410201','410202','410203','410204','410206','410207','410208','410209','410210','410216','410217','410218','410221','410222','410301','410302','410401','410402','410403','410405','410501','410502','410503','410504','410505','410506','410507','410515','410613','410614','410615','410707','411000','411001','411002','411003','411004','411005','411006','411007','411008','411009','411010','411011','411012','411013','411014','411015','411016','411017','411018','411019','411020','411021','411022','411023','411024','411025','411026','411027','411028','411029','411030','411031','411032','411033','411034','411035','411036','411037','411038','411039','411040','411041','411042','411043','411044','411045','411046','411047','411048','411049','411050','411051','411052','411053','411054','411055','411056','411057','411058','411060','411061','411111','411201','412000','412001','412101','412105','412106','412107','412108','412109','412110','412111','412112','412113','412114','412201','412202','412205','412206','412207','412208','412209','412210','412211','412212','412213','412215','412216','412217','412220','412301','412302','412303','412306','412307','412308','412501','412507','412801','412802','412803','412804','412805','412806','412903','413001','413002','413003','413004','413005','413006','413007','413101','413102','413105','413106','413107','413108','413109','413112','413113','413114','413118','413133','413201','413216','413255','413304','413401','413501','413512','413517','413521','413705','413706','413709','413710','413712','413713','413722','413736','413802','414001','414002','414003','414004','414005','414006','414110','414111','414113','415001','415002','415003','415004','415010','415011','415012','415105','415106','415108','415109','415110','415114','415124','415202','415205','415206','415311','415409','415501','415502','415505','415506','415508','415509','415510','415511','415512','415514','415515','415519','415521','415522','415523','415539','415603','415604','415605','415606','415608','415609','415610','415611','415612','415629','415630','415639','415709','415712','415722','415801','415804','416001','416002','416003','416004','416005','416006','416007','416008','416009','416010','416011','416012','416013','416101','416103','416109','416112','416113','416114','416115','416116','416117','416119','416121','416122','416129','416144','416201','416202','416203','416205','416207','416212','416216','416234','416301','416302','416303','416304','416306','416308','416309','416310','416311','416312','416405','416406','416410','416414','416415','416416','416417','416436','416502','416510','416516','416518','416520','416528','416602','416606','416613','416702','418101','419209','421001','421002','421003','421004','421005','421032','421102','421103','421201','421202','421203','421204','421300','421301','421302','421303','421305','421306','421307','421308','421311','421312','421359','421401','421421','421501','421502','421503','421505','421506','421601','421602','421605','422001','422002','422003','422004','422005','422006','422007','422008','422009','422010','422011','422012','422013','422101','422102','422103','422105','422113','422201','422203','422206','422207','422209','422212','422213','422221','422401','422402','422403','422501','422605','423101','423104','423105','423109','423203','423601','424001','424002','424003','424004','424005','424006','424311','425001','425002','425003','425109','425201','425203','425412','431001','431002','431003','431004','431005','431006','431007','431008','431009','431010','431105','431107','431122','431133','431136','431150','431201','431203','431210','431213','431401','431402','431513','431517','431601','431602','431603','431604','431605','431606','431803','440001','440002','440003','440004','440005','440006','440007','440008','440009','440010','440011','440012','440013','440014','440015','440016','440017','440018','440019','440020','440021','440022','440023','440024','440025','440026','440027','440028','440029','440030','440032','440033','440034','440035','441001','441002','441102','441103','441104','441105','441106','441107','441108','441109','441110','441111','441122','441202','441204','441401','441402','441501','441601','441612','441614','441902','441904','441905','441906','441912','442001','442003','442005','442006','442102','442301','442401','442402','442403','442404','442501','442502','442507','442701','442902','442908','442917','444001','444002','444003','444004','444005','444104','444303','444441','444442','444444','444445','444601','444602','444603','444604','444605','444606','444607','444701','444709','444710','445001','445003','450001','450331','451001','451551','452001','452002','452003','452004','452005','452006','452007','452008','452009','452010','452011','452012','452013','452014','452015','452016','452017','452018','452019','452020','452023','452056','453115','453331','453441','453771','454001','454545','454772','454774','454775','455001','455002','455003','455111','455336','456001','456003','456004','456005','456006','456007','456008','456009','456010','456331','456550','457001','457002','457112','457550','457661','458001','458002','458441','458470','460001','460002','460004','461001','461005','461111','461114','461115','461331','462001','462002','462003','462004','462005','462006','462007','462008','462010','462011','462012','462013','462014','462015','462016','462017','462018','462019','462021','462022','462023','462024','462025','462026','462027','462028','462029','462030','462031','462032','462034','462035','462036','462037','462038','462039','462040','462041','462042','462043','462046','462047','462048','464001','464002','464010','464221','464551','465001','465331','465445','465661','466001','466002','466011','470001','470002','470003','470004','470113','470661','471001','471606','472001','473001','473002','473111','473112','473113','473226','473331','473551','473638','473885','474001','474002','474003','474004','474005','474006','474007','474008','474009','474010','474011','474012','474020','475110','476001','476337','477001','477116','477117','480001','480106','480661','481001','481661','481880','482001','482002','482003','482004','482005','482006','482007','482008','482009','482010','482011','482020','482050','482051','482053','482056','483001','483501','483503','483504','483507','483880','484001','484661','485001','485002','485003','485004','485005','485771','486001','486002','486003','486005','486006','486114','486440','486448','486450','486661','486884','486885','486886','486887','486888','486889','486890','486892','486894','487001','487221','487551','488001','490001','490006','490009','490010','490011','490012','490013','490020','490021','490022','490023','490024','490025','490026','490027','490028','490036','490042','490401','491001','491002','491003','491004','491441','491504','491559','492001','492002','492003','492004','492005','492006','492007','492008','492009','492010','492011','492012','492013','492015','492042','492099','493004','493113','493114','493118','493221','493331','493445','493773','494001','494002','494005','494010','494553','494556','495001','495004','495005','495006','495009','495223','495334','495450','495452','495454','495671','495677','495678','495679','495680','495681','495682','495683','495684','495685','495686','496001','496004','497001','497442','500001','500002','500003','500004','500005','500006','500007','500008','500009','500010','500011','500012','500013','500014','500015','500016','500017','500018','500019','500020','500021','500022','500023','500024','500025','500026','500027','500028','500029','500030','500031','500032','500033','500034','500035','500036','500037','500038','500039','500040','500041','500042','500043','500044','500045','500046','500047','500048','500049','500050','500051','500052','500053','500054','500055','500056','500057','500058','500059','500060','500061','500062','500063','500064','500065','500066','500067','500068','500069','500070','500071','500072','500073','500074','500075','500076','500077','500078','500079','500080','500081','500082','500083','500084','500085','500086','500087','500088','500089','500090','500091','500092','500093','500094','500095','500096','500097','500098','500123','500146','500170','500177','500178','500195','500252','500253','500264','500265','500267','500361','500380','500409','500457','500475','500482','500484','500486','500556','500594','500659','500661','500762','500855','500872','500873','500890','500991','501203','501218','501301','501323','501401','501504','501505','501507','501510','501511','501512','502001','502032','502103','502108','502110','502220','502286','502291','502302','502307','502311','502313','502319','502324','502325','502329','502381','503001','503002','503003','503111','503122','503175','503185','503212','503224','503245','503306','503307','503310','504001','504103','504106','504201','504203','504205','504208','504215','504231','504251','504293','504296','504307','504311','505001','505002','505122','505172','505184','505209','505301','505302','505325','505326','505327','505404','505425','505460','505467','505468','506001','506002','506003','506004','506005','506006','506007','506008','506009','506010','506011','506012','506013','506015','506101','506132','506143','506163','506164','506167','506343','507001','507002','507003','507004','507101','507111','507115','507117','507123','507126','507133','507136','507165','507167','507203','507209','507301','507303','508001','508114','508116','508204','508206','508207','508213','508223','508248','508252','508277','509001','509002','509102','509103','509104','509125','509127','509208','509209','509210','509216','509301','509321','509324','509375','509381','515001','515002','515003','515004','515005','515110','515133','515134','515201','515231','515301','515401','515408','515411','515511','515591','515661','515671','515761','515775','515801','515812','515865','515871','516001','516002','516003','516004','516101','516104','516115','516172','516193','516227','516269','516289','516309','516329','516360','516361','516380','516390','516434','517001','517002','517003','517004','517012','517101','517102','517112','517125','517127','517128','517129','517131','517214','517234','517236','517247','517299','517325','517370','517408','517416','517424','517425','517501','517502','517503','517504','517505','517506','517507','517520','517583','517590','517592','517644','518001','518002','518003','518004','518005','518006','518101','518112','518123','518124','518134','518221','518222','518301','518313','518345','518360','518380','518395','518401','518422','518464','518501','518503','518510','518533','518543','518553','518599','520000','520001','520002','520003','520004','520005','520006','520007','520008','520009','520010','520011','520012','520013','520014','520015','521001','521101','521103','521104','521105','521108','521120','521121','521126','521137','521157','521165','521175','521178','521180','521185','521201','521212','521215','521225','521228','521230','521235','521286','521301','521324','521328','521333','521366','521456','522001','522002','522003','522004','522005','522006','522007','522009','522010','522019','522020','522022','522034','522101','522124','522201','522202','522233','522236','522265','522306','522313','522403','522413','522414','522415','522426','522438','522501','522503','522509','522510','522601','522616','522619','522647','523001','523002','523101','523105','523108','523155','523156','523157','523167','523184','523201','523212','523230','523240','523247','523253','523303','523316','523327','523333','523357','523373','524001','524002','524003','524004','524005','524006','524101','524121','524126','524132','524137','524201','524224','524226','524228','524305','524306','524308','524311','524313','524316','524320','524321','524322','524341','524344','524346','524401','530000','530001','530002','530003','530004','530005','530006','530007','530008','530009','530010','530011','530012','530013','530014','530015','530016','530017','530018','530019','530020','530021','530022','530023','530024','530025','530026','530027','530028','530029','530030','530031','530032','530033','530034','530035','530036','530037','530038','530039','530040','530041','530042','530043','530044','530045','530046','530047','530048','531001','531002','531011','531020','531021','531024','531027','531031','531036','531055','531081','531105','531111','531113','531116','531162','531163','531173','531201','532001','532002','532003','532004','532005','532127','532168','532185','532195','532201','532213','532216','532221','532242','532243','532263','532284','532312','532322','532405','532409','532421','532427','532440','532455','532456','532459','532460','533001','533002','533003','533004','533005','533006','533007','533008','533016','533020','533101','533102','533103','533104','533105','533106','533107','533124','533125','533126','533201','533212','533214','533216','533233','533238','533240','533241','533242','533251','533253','533255','533260','533262','533286','533287','533288','533289','533308','533341','533342','533344','533401','533406','533428','533429','533432','533435','533436','533437','533440','533445','533450','533464','534001','534002','534003','534004','534005','534006','534101','534102','534112','534122','534123','534134','534198','534199','534201','534202','534203','534204','534208','534211','534215','534235','534238','534245','534260','534264','534275','534280','534281','534301','534312','534313','534315','534320','534328','534341','534342','534350','534425','534426','534447','534449','534460','534462','535001','535002','535003','535004','535101','535128','535145','535183','535270','535501','535524','535547','535558','535591','560001','560002','560003','560004','560005','560006','560007','560008','560009','560010','560011','560012','560013','560014','560015','560016','560017','560018','560019','560020','560021','560022','560023','560024','560025','560026','560027','560028','560029','560030','560031','560032','560033','560034','560035','560036','560037','560038','560039','560040','560041','560042','560043','560044','560045','560046','560047','560048','560049','560050','560051','560052','560053','560054','560055','560056','560057','560058','560059','560060','560061','560062','560063','560064','560065','560066','560067','560068','560069','560070','560071','560072','560073','560074','560075','560076','560077','560078','560079','560080','560081','560082','560083','560084','560085','560086','560087','560088','560089','560090','560091','560092','560093','560094','560095','560096','560097','560098','560099','560100','560102','560103','560104','560105','560106','560109','560168','560300','560999','561203','561228','562106','562107','562109','562110','562111','562114','562122','562123','562125','562145','562147','562149','562157','562158','562159','562300','563101','563102','563113','563114','563115','563117','563118','563120','563122','563125','563130','565657','565658','570001','570002','570003','570004','570005','570006','570007','570008','570009','570010','570011','570012','570013','570014','570015','570016','570017','570018','570019','570020','570021','570022','570023','570024','570025','570026','570027','570301','570323','571105','571111','571124','571130','571186','571187','571201','571213','571234','571253','571301','571302','571304','571311','571313','571325','571401','571402','571403','571423','571438','571511','572101','572102','572103','572104','572105','572106','572107','572108','572120','572129','572130','572132','572168','572201','572202','572213','573102','573201','574104','574105','574106','574115','574116','574117','574118','574142','574143','574145','574146','574148','574150','574151','574154','574158','574159','574160','574161','574183','574194','574199','574201','574202','574203','574211','574212','574219','574220','574222','574227','574231','574239','574258','574325','574326','575001','575002','575003','575004','575005','575006','575007','575008','575009','575010','575011','575012','575013','575014','575015','575016','575017','575018','575019','575020','575021','575022','575023','575024','575025','575026','575028','575030','575152','575159','575211','576001','576025','576101','576102','576103','576104','576105','576106','576107','576108','576110','576113','576114','576118','576119','576125','576200','576201','576210','576213','576218','576225','577001','577002','577003','577004','577005','577006','577101','577102','577201','577202','577203','577204','577301','577302','577401','577427','577432','577501','577502','577522','577535','577547','577601','580001','580002','580003','580004','580005','580006','580007','580008','580009','580010','580011','580013','580020','580021','580022','580023','580024','580025','580026','580027','580028','580029','580030','580031','580032','580114','581106','581110','581115','581118','581123','581201','581202','581203','581301','581302','581303','581304','581314','581320','581401','581402','582101','582103','582205','583101','583102','583103','583104','583119','583123','583201','583202','583203','583204','583211','583212','583225','583227','583231','583233','583273','583275','583727','584101','584102','584103','584104','584105','584122','584123','584128','585101','585102','585103','585104','585105','585106','585201','585202','585223','585225','585228','585229','585317','585326','585328','585330','585401','585402','585403','586101','586102','586103','586104','586105','586106','586107','586108','587101','587102','587103','587107','587301','590001','590002','590003','590004','590005','590006','590007','590008','590009','590010','590011','590012','590013','590014','590015','590016','590018','591103','591108','591113','591123','591124','591135','591181','591201','591224','591225','591237','591306','591307','591308','591309','591313','600001','600002','600003','600004','600005','600006','600007','600008','600009','600010','600011','600012','600013','600014','600015','600016','600017','600018','600019','600020','600021','600022','600023','600024','600025','600026','600027','600028','600029','600030','600031','600032','600033','600034','600035','600036','600037','600038','600039','600040','600041','600042','600043','600044','600045','600046','600047','600048','600049','600050','600051','600052','600053','600054','600055','600056','600057','600058','600059','600060','600061','600062','600063','600064','600065','600066','600067','600068','600069','600070','600071','600072','600073','600074','600075','600076','600077','600078','600079','600080','600081','600082','600083','600084','600085','600086','600087','600088','600089','600090','600091','600092','600093','600094','600095','600096','600097','600098','600099','600100','600101','600102','600103','600104','600105','600106','600107','600108','600109','600110','600111','600112','600113','600114','600115','600116','600117','600118','600119','600120','600121','600122','600123','600125','600126','601101','601102','601103','601201','601202','601203','601204','601205','601206','601212','601301','601302','602001','602002','602003','602004','602021','602023','602024','602025','602026','602101','602102','602103','602104','602105','602106','602107','602108','602109','602117','603001','603002','603101','603102','603103','603104','603109','603110','603111','603112','603127','603201','603202','603203','603204','603209','603210','603301','603303','603306','603308','603312','603319','603406','604001','604002','604102','604151','604152','604153','604201','604202','604203','604204','604205','604206','604207','604208','604301','604302','604303','604304','604305','604306','604307','604401','604402','604403','604404','604405','604406','604407','604408','604409','604410','604411','604412','604413','604414','604415','604501','604601','605001','605002','605003','605004','605005','605006','605007','605008','605009','605010','605011','605012','605013','605014','605101','605102','605104','605105','605106','605107','605108','605109','605110','605111','605113','605120','605123','605201','605202','605203','605301','605401','605402','605501','605502','605601','605602','605604','605605','605606','605652','605702','605752','605753','605754','605756','605757','605759','605802','605809','606001','606002','606003','606102','606103','606104','606105','606106','606107','606108','606110','606111','606201','606202','606203','606204','606206','606207','606208','606301','606302','606304','606401','606402','606407','606601','606602','606603','606604','606611','606701','606702','606703','606704','606705','606706','606707','606708','606709','606710','606718','606751','606753','606754','606801','606802','606803','606807','606902','606903','606905','606906','607001','607002','607003','607004','607005','607006','607102','607103','607104','607105','607106','607107','607108','607109','607110','607204','607301','607302','607303','607401','607402','607801','607802','607803','607804','607807','608001','608002','608101','608102','608301','608302','608303','608305','608501','608502','608601','608602','608701','608702','608703','608704','608803','609001','609002','609003','609102','609103','609105','609109','609110','609111','609112','609114','609117','609201','609202','609203','609301','609307','609309','609311','609314','609401','609403','609404','609405','609501','609504','609601','609602','609603','609604','609605','609606','609607','609609','609702','609703','609801','609802','609803','609805','609806','609807','609810','610001','610002','610051','610101','610102','610105','610106','610109','610201','610204','610206','610207','610211','611001','611002','611101','611104','611105','611109','611110','611111','612001','612002','612101','612102','612103','612104','612107','612108','612201','612203','612204','612301','612302','612402','612502','612503','612504','612601','612602','612604','612605','612610','612701','612702','612703','612801','612802','612804','612904','613001','613002','613003','613004','613005','613006','613007','613008','613009','613010','613103','613104','613201','613204','613301','613303','613402','613403','613501','613502','613504','613701','613702','613703','613704','613705','613706','613707','614001','614010','614012','614013','614014','614015','614016','614017','614018','614019','614020','614021','614022','614023','614024','614025','614026','614027','614028','614029','614030','614031','614101','614102','614103','614201','614203','614204','614205','614206','614207','614208','614210','614211','614301','614302','614303','614401','614403','614404','614601','614602','614612','614613','614614','614615','614616','614617','614618','614619','614621','614622','614624','614625','614628','614701','614704','614707','614708','614711','614712','614713','614714','614715','614716','614717','614720','614721','614722','614723','614724','614725','614726','614727','614801','614802','614804','614806','614808','614809','614810','614818','614901','614902','614903','614904','614905','614906','614908','614909','614910','614911','614912','614913','614914','620001','620002','620003','620004','620005','620006','620007','620008','620009','620010','620011','620012','620013','620014','620015','620016','620017','620018','620019','620020','620021','620022','620023','620024','620025','620026','620101','620102','621001','621002','621003','621004','621005','621006','621007','621008','621010','621011','621012','621013','621014','621101','621102','621103','621104','621107','621108','621109','621110','621111','621112','621113','621114','621115','621116','621117','621118','621121','621126','621133','621203','621205','621206','621207','621208','621209','621210','621211','621212','621213','621214','621215','621216','621218','621219','621220','621301','621302','621303','621304','621305','621306','621307','621308','621309','621310','621311','621312','621314','621315','621316','621601','621620','621651','621652','621653','621701','621702','621703','621704','621705','621706','621707','621708','621709','621710','621711','621712','621713','621715','621716','621717','621729','621730','621801','621802','621803','621804','621806','621901','621904','622001','622002','622003','622004','622005','622101','622102','622103','622104','622105','622107','622201','622202','622203','622206','622207','622301','622302','622303','622304','622403','622407','622408','622411','622501','622502','622503','622504','622505','622506','622507','622508','622511','622512','622513','622514','622515','622521','622522','623120','623211','623302','623303','623317','623404','623406','623407','623408','623409','623501','623502','623504','623512','623513','623514','623517','623518','623519','623521','623522','623523','623524','623525','623526','623527','623528','623529','623531','623534','623535','623536','623542','623546','623560','623603','623611','623613','623701','623702','623703','623704','623705','623706','623707','623708','623710','623712','623719','623806','624001','624002','624003','624004','624005','624006','624007','624008','624009','624010','624101','624102','624103','624104','624109','624201','624202','624203','624204','624206','624208','624209','624210','624211','624214','624215','624218','624219','624220','624221','624234','624301','624302','624304','624306','624308','624401','624403','624414','624601','624603','624610','624612','624613','624614','624615','624616','624617','624618','624619','624620','624621','624622','624701','624702','624703','624704','624705','624708','624709','624710','624711','624712','624801','624802','624803','625001','625002','625003','625004','625005','625006','625007','625008','625009','625010','625011','625012','625013','625014','625015','625016','625017','625018','625019','625020','625021','625022','625101','625102','625103','625104','625105','625106','625107','625108','625109','625110','625112','625113','625118','625122','625123','625124','625125','625126','625218','625221','625301','625401','625402','625501','625502','625503','625512','625513','625514','625516','625518','625522','625531','625532','625533','625534','625537','625566','625571','625602','625603','625606','625623','625703','625706','626001','626002','626003','626004','626005','626100','626101','626102','626104','626105','626106','626107','626108','626109','626110','626111','626112','626113','626114','626115','626117','626118','626119','626120','626121','626123','626124','626125','626126','626128','626129','626130','626131','626132','626133','626138','626139','626141','626142','626144','626146','626148','626149','626150','626151','626152','626153','626154','626155','626159','626160','626164','626167','626170','626177','626178','626188','626189','626201','626203','626204','626205','626213','626313','626512','626513','626515','626521','626526','626531','626532','626556','626601','626605','626606','626607','626639','626706','627001','627002','627003','627004','627005','627006','627007','627008','627009','627010','627011','627101','627102','627103','627104','627105','627106','627107','627109','627110','627111','627113','627114','627115','627116','627117','627120','627121','627122','627124','627128','627152','627201','627202','627252','627352','627353','627357','627358','627401','627413','627414','627415','627416','627417','627418','627422','627423','627424','627425','627426','627427','627428','627431','627433','627435','627436','627451','627453','627501','627502','627601','627604','627716','627719','627726','627751','627753','627754','627755','627756','627757','627758','627759','627760','627761','627762','627763','627764','627766','627767','627768','627769','627773','627801','627802','627803','627804','627805','627806','627807','627808','627809','627810','627811','627812','627813','627814','627815','627816','627817','627818','627819','627820','627822','627823','627851','627852','627853','627855','627856','627857','627858','627859','627861','627862','627904','627905','627906','627907','627909','627910','627912','627951','627953','627954','627955','627956','627957','628001','628002','628003','628004','628005','628006','628007','628008','628101','628103','628105','628151','628152','628201','628202','628203','628204','628205','628206','628207','628208','628209','628210','628211','628213','628214','628215','628216','628217','628218','628219','628220','628221','628222','628223','628224','628225','628226','628227','628228','628229','628251','628252','628313','628401','628402','628501','628502','628503','628601','628611','628612','628613','628614','628615','628616','628617','628618','628619','628620','628621','628622','628623','628626','628628','628629','628630','628631','628651','628653','628701','628702','628703','628704','628705','628706','628707','628722','628751','628752','628753','628801','628802','628803','629001','629002','629003','629004','629101','629102','629103','629151','629152','629153','629154','629155','629156','629157','629158','629159','629160','629161','629162','629163','629164','629165','629166','629167','629168','629169','629170','629171','629172','629173','629174','629175','629176','629177','629178','629179','629180','629181','629182','629183','629187','629188','629189','629190','629191','629192','629193','629197','629201','629203','629251','629252','629301','629302','629304','629305','629401','629402','629403','629501','629601','629701','629702','629703','629708','629802','629803','629804','629805','629807','629851','629852','629901','630001','630003','630004','630005','630101','630102','630103','630107','630108','630201','630203','630204','630206','630207','630211','630301','630302','630303','630309','630310','630311','630312','630313','630314','630315','630318','630401','630405','630413','630502','630551','630552','630553','630556','630557','630560','630561','630562','630565','630606','630607','630611','630615','631001','631002','631003','631004','631005','631006','631051','631052','631056','631057','631059','631060','631101','631102','631103','631151','631203','631205','631207','631208','631209','631210','631213','631501','631502','631503','631504','631505','631551','631552','631555','631556','631557','631558','631561','631601','631605','631606','631607','631702','632001','632002','632003','632004','632005','632006','632007','632008','632009','632010','632011','632012','632013','632014','632052','632053','632054','632055','632057','632058','632059','632101','632102','632103','632104','632105','632106','632107','632108','632114','632201','632202','632203','632204','632207','632209','632301','632311','632313','632315','632316','632317','632318','632319','632401','632402','632403','632404','632405','632406','632501','632503','632504','632505','632506','632507','632508','632509','632511','632512','632513','632514','632515','632516','632517','632519','632521','632531','632601','632602','632603','632604','632605','632606','632607','632608','635001','635002','635101','635103','635105','635106','635107','635108','635109','635110','635111','635112','635113','635114','635117','635118','635119','635125','635126','635202','635205','635206','635207','635303','635305','635601','635602','635611','635701','635708','635751','635752','635753','635754','635755','635756','635801','635802','635803','635804','635805','635806','635807','635808','635809','635810','635811','635812','635813','635814','635815','635820','635821','635825','635826','635851','636001','636002','636003','636004','636005','636006','636007','636008','636009','636010','636011','636012','636013','636014','636015','636016','636020','636030','636102','636103','636104','636105','636106','636107','636108','636109','636110','636111','636112','636113','636114','636115','636116','636117','636118','636119','636121','636122','636140','636141','636201','636202','636203','636204','636301','636302','636303','636304','636305','636306','636307','636308','636401','636402','636403','636404','636406','636453','636454','636455','636456','636457','636501','636502','636503','636601','636602','636701','636702','636703','636704','636705','636806','636807','636808','636810','636813','636903','636904','636905','636906','636908','637001','637002','637003','637013','637015','637017','637018','637019','637020','637021','637022','637023','637024','637025','637026','637103','637104','637112','637201','637202','637203','637204','637205','637206','637207','637209','637210','637211','637212','637213','637214','637303','637305','637401','637402','637403','637404','637405','637406','637407','637408','637409','637410','637412','637413','637414','637415','637418','637422','637423','637501','637502','637503','637504','637505','637507','638001','638002','638003','638004','638005','638006','638007','638008','638009','638010','638011','638051','638052','638053','638054','638055','638056','638057','638058','638060','638101','638102','638103','638104','638105','638106','638107','638108','638109','638110','638111','638112','638113','638115','638116','638118','638151','638153','638154','638157','638181','638182','638183','638301','638302','638303','638311','638312','638313','638314','638315','638327','638401','638402','638451','638452','638453','638454','638455','638456','638457','638458','638459','638460','638461','638464','638476','638501','638502','638503','638505','638506','638653','638656','638657','638658','638660','638661','638672','638673','638697','638701','638702','638703','638706','638751','638752','638812','639001','639002','639003','639004','639005','639006','639007','639051','639101','639102','639104','639105','639106','639107','639108','639109','639111','639112','639113','639114','639116','639117','639118','639136','639201','639202','639205','639206','639207','641001','641002','641003','641004','641005','641006','641007','641008','641009','641010','641011','641012','641013','641014','641015','641016','641017','641018','641019','641020','641021','641022','641023','641024','641025','641026','641027','641028','641029','641030','641031','641032','641033','641034','641035','641036','641037','641038','641039','641040','641041','641042','641043','641044','641045','641046','641047','641048','641062','641065','641101','641102','641103','641104','641105','641106','641107','641108','641109','641110','641111','641112','641113','641114','641115','641116','641117','641201','641202','641301','641302','641305','641401','641402','641403','641404','641405','641406','641407','641408','641601','641602','641603','641604','641605','641606','641607','641608','641610','641642','641652','641653','641654','641655','641658','641659','641662','641663','641664','641665','641666','641667','641668','641669','641670','641671','641687','641697','642001','642002','642003','642004','642005','642006','642007','642102','642103','642104','642106','642107','642108','642109','642110','642111','642112','642113','642114','642117','642118','642120','642122','642123','642126','642127','642128','642129','642130','642131','642132','642133','642134','642139','642153','642154','642201','642204','642205','642206','642215','642218','642401','643001','643002','643003','643004','643005','643006','643007','643101','643102','643103','643104','643105','643201','643202','643203','643205','643207','643211','643212','643213','643214','643215','643216','643217','643218','643219','643221','643222','643223','643224','643225','643226','643229','643231','643232','643234','643237','643239','643240','643241','643242','643243','643265','643271','643272','643276','670001','670002','670003','670004','670005','670006','670007','670008','670009','670010','670011','670012','670013','670014','670015','670016','670017','670101','670102','670103','670104','670107','670141','670307','670565','670592','670597','670645','670672','671121','671123','671124','671314','671315','671317','671318','671323','671531','671541','673001','673002','673003','673004','673005','673006','673007','673008','673009','673010','673011','673012','673013','673014','673015','673016','673017','673018','673020','673021','673024','673025','673026','673027','673031','673032','673037','673101','673121','673122','673502','673579','673592','673631','673632','673633','673634','673635','673638','676102','676107','676121','676122','676309','676311','676312','676319','676501','676503','676504','676505','676506','676507','676509','676519','676522','676541','676542','676553','676561','676562','678001','678002','678003','678004','678005','678006','678007','678008','678009','678010','678011','678012','678013','678014','678582','678583','678601','678621','678623','679121','679123','679307','679321','679322','679324','679326','679333','679334','679338','679503','679571','679572','679576','679577','679581','679587','679591','680001','680002','680003','680004','680005','680006','680007','680008','680009','680010','680011','680012','680013','680014','680018','680020','680021','680022','680026','680027','680121','680122','680125','680302','680306','680307','680308','680503','680507','680517','680567','680651','680655','680662','680664','680666','680667','680668','680669','680683','680684','680688','680689','680712','680721','680731','680736','680751','682001','682002','682003','682004','682005','682006','682007','682009','682010','682011','682012','682013','682014','682015','682016','682017','682018','682019','682020','682021','682022','682023','682024','682025','682026','682027','682028','682029','682030','682031','682032','682033','682034','682035','682036','682037','682038','682039','682040','682041','682301','682302','682303','682304','682305','682309','682311','682314','682503','682506','682507','683101','683102','683103','683104','683105','683106','683108','683109','683110','683501','683503','683511','683515','683561','683562','683564','683572','683573','683574','683585','685501','685509','685535','685553','685585','686001','686002','686003','686004','686005','686006','686008','686009','686010','686012','686013','686016','686019','686038','686039','686101','686107','686121','686507','686575','686619','686631','686633','686661','686673','686680','686691','688001','688002','688003','688004','688005','688006','688007','688008','688009','688010','688011','688012','688013','688014','688521','688522','688523','688524','688525','688527','688531','688534','688537','688539','688542','689101','689107','689511','689672','689695','690101','690109','690514','690518','690526','690548','691001','691002','691003','691004','691005','691006','691007','691008','691009','691010','691011','691012','691013','691014','691016','691017','691019','691020','691306','691332','691501','691506','691523','691552','691554','691571','691605','694582','695001','695002','695003','695004','695005','695006','695007','695008','695009','695010','695011','695012','695013','695014','695015','695016','695017','695018','695019','695021','695022','695023','695024','695025','695026','695027','695029','695030','695031','695032','695033','695034','695035','695036','695037','695038','695039','695040','695041','695043','695044','695049','695101','695121','695521','695523','695524','695527','695547','695581','695582','695583','695586','695601','700001','700002','700003','700004','700005','700006','700007','700008','700009','700010','700011','700012','700013','700014','700015','700016','700017','700018','700019','700020','700021','700022','700023','700024','700025','700026','700027','700028','700029','700030','700031','700032','700033','700034','700035','700036','700037','700038','700039','700040','700041','700042','700043','700044','700045','700046','700047','700048','700049','700050','700051','700052','700053','700054','700055','700056','700057','700058','700059','700060','700061','700062','700063','700064','700065','700066','700067','700068','700069','700070','700071','700072','700073','700074','700075','700076','700077','700078','700079','700080','700081','700082','700083','700084','700085','700086','700087','700088','700089','700090','700091','700092','700093','700094','700095','700096','700097','700098','700099','700100','700101','700102','700103','700104','700105','700106','700107','700108','700109','700110','700111','700112','700113','700114','700115','700116','700117','700118','700119','700120','700121','700122','700123','700124','700125','700126','700127','700128','700129','700130','700131','700132','700133','700134','700135','700136','700137','700138','700139','700140','700141','700142','700143','700144','700145','700146','700147','700148','700149','700150','700151','700152','700153','700154','700155','700156','700157','701101','711101','711102','711103','711104','711105','711106','711107','711108','711109','711110','711112','711113','711114','711201','711202','711203','711204','711227','711302','711303','711304','711306','711308','711310','711312','711313','711316','711322','711325','711402','711403','711405','712101','712102','712103','712104','712123','712124','712125','712136','712137','712148','712149','712201','712202','712203','712204','712205','712221','712222','712223','712232','712233','712234','712235','712245','712246','712248','712249','712250','712258','712401','712403','712405','712407','712409','712410','712502','712503','712601','712613','712702','713101','713102','713103','713104','713124','713125','713126','713127','713128','713130','713140','713144','713146','713147','713148','713149','713151','713152','713167','713201','713202','713203','713204','713205','713206','713207','713208','713209','713210','713211','713212','713213','713214','713215','713216','713217','713218','713219','713301','713302','713303','713304','713315','713321','713322','713324','713325','713331','713333','713334','713336','713338','713339','713342','713343','713347','713357','713358','713359','713364','713365','713369','713371','713378','713380','713384','713385','713403','713404','713406','713407','713408','713409','713421','713422','713423','713424','713502','713512','721060','721101','721102','721124','721126','721127','721130','721132','721134','721136','721137','721139','721143','721145','721147','721151','721152','721153','721154','721169','721171','721201','721211','721212','721222','721232','721301','721302','721303','721304','721305','721306','721401','721422','721423','721424','721425','721426','721427','721428','721429','721430','721431','721432','721433','721434','721436','721439','721441','721444','721445','721447','721448','721449','721452','721453','721455','721458','721461','721467','721502','721507','721516','721601','721602','721603','721604','721605','721606','721607','721628','721629','721631','721632','721633','721635','721636','721641','721645','721648','721650','721651','721654','721657','721658','721659','721663','721668','721670','722101','722102','722122','722132','722138','722140','722141','722158','722183','722202','722203','722205','722207','723101','723102','723103','723121','723131','723133','723143','723146','723157','723202','731101','731102','731103','731121','731123','731127','731132','731201','731204','731216','731219','731220','731224','731233','731234','731235','731236','731237','731243','731303','732101','732102','732103','732121','732122','732123','732124','732128','732139','732141','732142','732143','732201','732206','732208','732211','732215','732216','732236','733101','733102','733103','733123','733124','733129','733130','733134','734001','734002','734003','734004','734005','734006','734007','734008','734010','734013','734015','734101','734104','734203','734301','734401','734402','734403','734404','734405','734406','734421','734422','734423','734426','734428','734429','734433','734434','734435','735101','735102','735204','735210','735215','736101','736121','736122','736123','736135','736136','736146','736159','736182','737101','737102','737132','741101','741102','741103','741121','741126','741156','741201','741202','741222','741232','741234','741235','741245','741246','741247','741250','741251','741302','741313','741402','741404','742101','742102','742103','742123','742133','742134','742135','742137','742147','742148','742149','742187','742188','742202','742212','742225','742236','742262','743122','743123','743124','743125','743126','743127','743128','743129','743133','743134','743135','743136','743144','743145','743165','743166','743194','743222','743232','743233','743235','743245','743248','743251','743263','743269','743270','743272','743273','743276','743287','743289','743291','743401','743411','743426','743428','743429','743437','743445','743503','743704','743706','744101','744102','744103','744104','751001','751002','751003','751004','751005','751006','751007','751008','751009','751010','751011','751012','751013','751014','751015','751016','751017','751018','751019','751020','751021','751022','751023','751024','751025','751026','751027','751028','751029','751030','751031','752001','752002','752050','752055','752057','752069','752101','753001','753002','753003','753004','753005','753006','753007','753008','753009','753010','753011','753012','753013','753014','753021','753051','753071','754005','754021','754025','754028','754070','754071','754103','754120','754142','754143','754145','754211','754221','755001','755008','755019','755020','755022','755026','755040','755044','756001','756002','756003','756019','756025','756056','756100','756101','756135','756181','757001','757002','757003','758001','758034','758035','758037','759001','759013','759031','759100','759101','759103','759106','759107','759116','759117','759122','759123','759128','759132','759143','759145','759147','760001','760002','760003','760004','760005','760006','760007','760008','760009','760010','760011','761002','761011','761020','761025','761026','761045','761200','761201','761213','763001','763002','763003','763008','764001','764003','764004','764020','764036','765001','765002','765017','765018','765020','765022','766001','766020','766027','766105','767001','767002','768001','768002','768003','768004','768016','768017','768018','768019','768020','768028','768038','768102','768103','768104','768105','768108','768150','768201','768202','768203','768204','768205','768216','768217','768218','769001','769002','769003','769004','769005','769006','769007','769008','769009','769010','769011','769012','769013','769014','769015','769016','769041','769042','769043','770001','770017','770031','770032','770034','770037','781001','781002','781003','781004','781005','781006','781007','781008','781009','781010','781011','781012','781013','781014','781015','781016','781017','781018','781019','781020','781021','781022','781023','781024','781025','781026','781027','781028','781029','781030','781031','781032','781033','781034','781035','781036','781037','781038','781039','781071','781171','781315','782001','782002','782410','782435','782460','783301','783302','783303','783304','783305','783306','783307','783308','783309','783310','783311','783312','783313','783314','783315','783316','783317','783318','783319','783320','783321','783322','783323','783331','783370','783380','783381','783385','784001','784028','784101','784115','784176','785001','785002','785004','785005','785006','785007','785008','785009','785010','785013','785014','785101','785107','785612','785614','785621','785630','785631','785632','785633','785634','785635','785640','785660','785662','785664','785669','785670','785673','785680','785681','785685','785686','785690','785696','785699','785704','786001','786002','786003','786004','786005','786006','786007','786008','786012','786124','786125','786126','786145','786146','786147','786151','786170','786171','786181','786184','786602','786610','786621','786623','787001','788001','788002','788003','788004','788005','788006','788007','788009','788010','788015','788151','788710','788711','788712','788803','788805','788819','791109','791110','791111','791113','792110','793001','793002','793003','793004','793005','793011','793014','793150','793151','793200','795001','795002','795003','795004','795008','796001','796005','796007','796012','797001','797112','797113','797114','797115','797116','797117','799001','799002','799003','799004','799005','799006','799007','799008','799009','799010','799014','799250','799253','799264','799277','799279','800001','800002','800003','800004','800005','800006','800007','800008','800009','800010','800011','800012','800013','800014','800015','800016','800017','800018','800019','800020','800021','800022','800023','800024','800025','800026','800027','800028','801105','801109','801503','801505','802101','802102','802103','802301','802304','803101','803116','803118','803213','803214','803302','803303','804408','804417','805110','811201','811202','811214','812001','812002','812003','812004','812005','812006','812007','813203','813210','813214','815301','815302','815303','815304','815305','815316','815351','816107','816109','821101','821109','821113','821115','821305','821307','822101','822102','822114','823001','823002','823003','823004','823005','824231','825301','825303','825314','825316','825401','825409','826001','826002','826003','826004','826005','826006','826015','826106','827001','827002','827003','827004','827005','827006','827007','827008','827009','827010','827011','827012','827013','827014','827611','828101','828104','828105','828106','828107','828108','828109','828110','828111','828112','828113','828114','828115','828116','828117','828119','828120','828121','828122','828123','828124','828127','828129','828130','828131','828132','828135','828147','828202','828203','828205','828207','828301','828302','828304','829107','829117','829118','829119','829122','829130','829131','829144','829206','831001','831002','831003','831004','831005','831006','831007','831008','831009','831010','831011','831012','831013','831014','831015','831016','831017','831018','831019','831035','832003','832102','832104','832106','832107','832108','832109','832110','832301','832303','833102','833201','833215','833217','833218','833219','833222','834001','834002','834003','834004','834005','834006','834007','834008','834009','834010','834011','834012','835103','835205','835207','835215','835217','835222','835223','835301','835302','835314','841226','841301','841428','842001','842002','842003','842004','842005','843001','843109','843116','843130','843301','843302','843611','844101','844121','845305','845311','845401','845408','845412','845424','845438','846001','846002','846003','846004','846005','846006','846009','847211','848101','848125','851101','851112','851113','851114','851115','851116','851117','851122','851126','851134','851135','851204','852113','852127','852131','852201','853204','854105','854106','854114','854301','854302','854303','854304','854305','854318','854326','855101','855106','855107']


		if bundle.data['pincode'] in goodpincodes:
			bundle.data['valid']=1
		else:
			bundle.data['valid']=0
			bundle.data['msg']='we dont have pickup service available in your desired pickup location.'

		return bundle
