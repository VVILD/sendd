from businessapp.models import Product
from import_export import resources
from import_export import fields
from datetime import timedelta
import json

class ProductResource(resources.ModelResource):

	class Meta:
		model = Product
		import_id_fields = ('order_id',)
		fields = ('order','order__book_time','order__reference_id','order__payment_method','order__name','order__city','order__pincode', 'real_tracking_no', 'mapped_tracking_no', 'company','status','last_tracking_status','weight','applied_weight','barcode','order__method')



class QcProductResource(resources.ModelResource):
	expected_delivery_date = fields.Field()
	last_location = fields.Field()
	
	class Meta:
		model = Product
		fields = ('order','order__book_time','order__name','order__city','order__pincode', 'real_tracking_no', 'mapped_tracking_no', 'company','applied_weight','dispatch_time','order__business','update_time','last_tracking_status')
		export_order = ('order', 'real_tracking_no','mapped_tracking_no','company','order__book_time','dispatch_time','order__book_time', 'order__name', 'update_time','last_tracking_status')

	def dehydrate_expected_delivery_date(self, product):
		if (product.order.method=='B'):
			return (product.date + timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")
		elif (product.order.method=='N'):
			return (product.date + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
		else:
			return 'None'

	def dehydrate_last_location(self, product):
		return json.loads(product.tracking_data)[-1]['location']



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

