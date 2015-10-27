from businessapp.models import Product,Order,Business
from import_export import resources
from import_export import fields
from datetime import timedelta
import json
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch
class ProductResource(resources.ModelResource):

	class Meta:
		model = Product
		import_id_fields = ('order_id',)
		fields = ('order','order__book_time','order__reference_id','order__payment_method','order__name','order__city','order__pincode', 'real_tracking_no', 'mapped_tracking_no', 'company','status','last_tracking_status','weight','applied_weight','barcode','order__method','name','price','remittance','remittance_date')


class CodBusinessResource(resources.ModelResource):
	amount = fields.Field()


	class Meta:
		model = Business
		fields = ('username','business_name','amount')

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
	company = fields.Field()
	no_of_products = fields.Field()

	class Meta:
		model = Order
		fields = ('order_no','book_time','business__business_name','city','pincode','mapped_ok','no_of_products','company','ff_comment')
		export_order = ('order_no','book_time','business__business_name','city','pincode','mapped_ok','no_of_products','company','ff_comment')

	def dehydrate_mapped_ok(self,order):
		products=Product.objects.filter(order=order)
		mapped_ok=True
		for product in products:
			if (not product.mapped_tracking_no):
				return False
		return mapped_ok


	def dehydrate_no_of_products(self, order):
		return Product.objects.filter(order=order).count()

	def dehydrate_company(self, order):
		try:
			return order.product_set.first().company
		except:
			return "no product"


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

