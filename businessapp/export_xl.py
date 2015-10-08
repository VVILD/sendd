from businessapp.models import Product
from import_export import resources

class ProductResource(resources.ModelResource):

    class Meta:
        model = Product
       	import_id_fields = ('order_id',)
        fields = ('order','order__book_time','order__name','order__city','order__pincode', 'real_tracking_no', 'mapped_tracking_no', 'company',)