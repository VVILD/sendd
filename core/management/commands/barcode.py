date_min = datetime.datetime.combine(date2, datetime.time.min)
date_max = datetime.datetime.combine(date2, datetime.time.max)
from businessapp.models import Order as BOrder

b2b = BOrder.objects.filter(
        Q(book_time__range=(date_min, date_max)))

product_barcode=Product.objects.filter(order=b2b,barcode__isnull=False).count()
product_total=Product.objects.filter(order=b2b).count()
percentage=(product_barcode/product_total)*100