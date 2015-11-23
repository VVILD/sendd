from businessapp.models import Product,Order,Business
from import_export import resources
from import_export import fields
from datetime import timedelta
import json
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch
class ProductResource(resources.ModelResource):
	# last_status = fields.Field()
	# last_date = fields.Field()
	class Meta:
		model = Product
		import_id_fields = ('order_id',)
		fields = ('order','order__book_time','order__reference_id','order__payment_method','order__name','order__city','order__pincode', 'real_tracking_no', 'mapped_tracking_no', 'company','status','last_tracking_status','weight','applied_weight','barcode','order__method','name','price','remittance','remittance_date','ff_comment','order__address1','order__address2')


	# def dehydrate_last_status(self, product):
	# 	return json.loads(product.tracking_data)[-1]['status']


	# def dehydrate_last_date(self, product):
	# 	return json.loads(product.tracking_data)[-1]['date']

	def dehydrate_ff_comment(self, product):
		return product.order.ff_comment

class BusinessResource(resources.ModelResource):

	class Meta:
		model = Business
		fields = ('username','business_name','email','warehouse__name','address','pincode','name')


class CodBusinessResource(resources.ModelResource):
	amount = fields.Field()
	class Meta:
		model = Business
		fields = ('username','business_name','amount','billed_to','account_name','account_type','bank_name','branch','ifsc_code')

	def dehydrate_amount(self, business):

		today_orders_b2b = Order.objects.filter(business=business,payment_method='C')

		query_complete=Product.objects.filter(order=today_orders_b2b,status='C',remittance_status='I')
		sum_complete = query_complete.aggregate(total=Sum('price'))['total']
		return sum_complete




class QcProductResource(resources.ModelResource):
	expected_delivery_date = fields.Field()
	last_location = fields.Field()
	
	class Meta:
		model = Product
		fields = ('order','order__book_time','order__name','order__city','order__pincode', 'real_tracking_no', 'mapped_tracking_no', 'company','applied_weight','dispatch_time','order__business','update_time','last_tracking_status','qc_comment')
		export_order = ('order', 'real_tracking_no','mapped_tracking_no','company','order__book_time','dispatch_time','order__book_time', 'order__name', 'update_time','last_tracking_status','qc_comment')

	def dehydrate_expected_delivery_date(self, product):
		if (product.order.method=='B'):
			return (product.date + timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")
		elif (product.order.method=='N'):
			return (product.date + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
		else:
			return 'None'

	def dehydrate_last_location(self, product):
		return json.loads(product.tracking_data)[-1]['location']




class FFOrderResource(resources.ModelResource):
	mapped_ok = fields.Field()
	no_of_products = fields.Field()
	cod_or_free= fields.Field()
	bulk_or_normal= fields.Field()
	dispatched_date  = fields.Field()
	company_list = fields.Field()
	tracking_list= fields.Field()

	class Meta:
		model = Order
		fields = ('tracking_list','company_list','dispatched_date','order_no','book_time','business__business_name','city','pincode','name','mapped_ok','no_of_products','bulk_or_normal','cod_or_free','ff_comment','address1','reference_id','address2')

	def dehydrate_bulk_or_normal(self,order):
		return order.get_method_display()

	def dehydrate_cod_or_free(self,order):
		return order.get_payment_method_display()


	def dehydrate_dispatched_date(self,order):
		products=Product.objects.filter(order=order)
		return_string=''
		for product in products:
			if (product.dispatch_time):
				return_string=return_string+str(product.dispatch_time)+','


		return return_string

	def dehydrate_company_list(self,order):
		products=Product.objects.filter(order=order)
		return_string=''
		for product in products:
			if (product.company):
				return_string=return_string+str(product.get_company_display())+','


		return return_string


	def dehydrate_tracking_list(self,order):
		products=Product.objects.filter(order=order)
		return_string=''
		for product in products:
			if (product.mapped_tracking_no):
				return_string=return_string+str(product.mapped_tracking_no)+','


		return return_string


	def dehydrate_mapped_ok(self,order):
		products=Product.objects.filter(order=order)
		mapped_ok=True
		for product in products:
			if (not product.mapped_tracking_no):
				return False
		return mapped_ok


	def dehydrate_no_of_products(self, order):
		return Product.objects.filter(order=order).count()



# 1.Order No.
# 2. Tracking No.
# 3. Company
# 4. Book date
# 5. Dispatch Time
# 6. Business
# 7. Send to
# 8. Tracking status
# 9. last location
# 10. Expected delivery date
# 11. Last updated on
# 12. last tracking status

