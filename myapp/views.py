from django.shortcuts import render

from myapp.models import *
# Create your views here.
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch
from businessapp.models import Order as BOrder
from businessapp.models import Product,Business

from django.http import HttpResponse

import datetime

from datetime import date
import datetime
from django.db.models import Avg
from pprint import pprint
from itertools import groupby

def index(request):
	todays_date=date.today()
	week_before=date.today()-datetime.timedelta(days=7)

# today min/max
	today_min = datetime.datetime.combine(todays_date, datetime.time.min)
	today_max = datetime.datetime.combine(todays_date, datetime.time.max)
	
#week min/max	
	date_min = datetime.datetime.combine(week_before, datetime.time.min)
	date_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
	
#customer stats today


	today_orders =Order.objects.filter(Q(book_time__range=(today_min,today_max))&(Q(status='P') | Q(status='C')))
	today_shipments_correct=Shipment.objects.filter(order=today_orders).exclude(price__isnull=True).exclude(price__exact='')
	today_shipments=Shipment.objects.filter(order=today_orders)
	average_b2c=today_shipments_correct.aggregate(Avg('price'))['price__avg']
	sum_b2c=today_shipments_correct.aggregate(Sum('price'))['price__sum']
	count_b2c=today_shipments_correct.count()
	action_b2c=today_shipments.count()-today_shipments_correct.count()
	
#customer stats week
	week_orders =Order.objects.filter(Q(book_time__range=(date_min,date_max))&(Q(status='P') | Q(status='C')))
	week_shipments=Shipment.objects.filter(order=week_orders).values('order__book_time','price').exclude(price__isnull=True).exclude(price__exact='')

	b2c_stats=[]
	for key, values in groupby(week_shipments, key=lambda row: row['order__book_time'].date()):
	    print('-')
	    #pprint(key)
	    x=list(values)
	    print len(x)
	    sum=0
	    for y in x:
	        sum=sum+int(y['price'])
	    print sum
	    b2c_stats.append([str(key),len(x),sum,sum/len(x)])

#business stats today
	today_orders_b2b=BOrder.objects.filter(Q(book_time__range=(today_min,today_max))&(Q(status='P') | Q(status='C')| Q(status='D')))
	today_products_correct=Product.objects.filter(order=today_orders_b2b).exclude(shipping_cost__isnull=True)
	today_products=Product.objects.filter(order=today_orders_b2b)
	average_b2b=today_products_correct.aggregate(total=Avg('shipping_cost', field="shipping_cost+cod_cost"))['total']
	sum_b2b=today_products_correct.aggregate(total=Sum('shipping_cost', field="shipping_cost+cod_cost"))['total']
	count_b2b=today_products_correct.count()
	action_b2b=today_products.count()-today_products_correct.count()

	
#b2b week
	week_orders_b2b =BOrder.objects.filter(Q(book_time__range=(date_min,date_max))&(Q(status='P') | Q(status='C')| Q(status='D')))
	week_products_b2b=Product.objects.filter(order=week_orders_b2b).values('order__book_time','shipping_cost','cod_cost').exclude(shipping_cost__isnull=True)
	b2b_stats=[]
	for key, values in groupby(week_products_b2b, key=lambda row: row['order__book_time'].date()):
	    print('-')
	    pprint(key)
	    x=list(values)
	    print len(x)
	    sum=0
	    for y in x:
	        sum=sum+int(y['shipping_cost']+y['cod_cost'])
	    print sum
	    b2b_stats.append([str(key),len(x),sum,sum/len(x)])





	
# business stats grouped by businesses
	product_groupedby_business=Product.objects.filter(order=today_orders_b2b).exclude(shipping_cost__isnull=True).values('order__business').annotate(total_revenue=Sum('shipping_cost', field="shipping_cost+cod_cost"), total_no=Count('order'))


	context = {'product_groupedby_business':product_groupedby_business,'average_b2c':average_b2c,'sum_b2c':sum_b2c,'count_b2c':count_b2c,'average_b2b':average_b2b,'sum_b2b':sum_b2b,'count_b2b':count_b2b,'b2c_stats':b2c_stats,'b2b_stats':b2b_stats,'action_b2b':action_b2b,'action_b2c':action_b2c}
	return render(request, 'polls/index.html', context)

	
def detail(request):

	todays_date=date.today()
	week_before=date.today()-datetime.timedelta(days=7)

# today min/max
	
#week min/max	
	date_min = datetime.datetime.combine(week_before, datetime.time.min)
	date_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
	
#customer stats today

	
#customer stats week
	week_orders =Order.objects.filter(Q(book_time__range=(date_min,date_max))&(Q(order_status='O') | Q(order_status='A')| Q(order_status='P')| Q(order_status='Pa')| Q(order_status='C')| Q(order_status='D') | Q(order_status='Q')))
	week_shipments=Shipment.objects.filter(Q(order=week_orders)&(Q(mapped_tracking_no__isnull=True)|Q(mapped_tracking_no__exact='')))


#business stats today

	
#b2b week
	week_orders_b2b =BOrder.objects.filter(Q(book_time__range=(date_min,date_max))&(Q(status='P') | Q(status='C')| Q(status='D')))
	week_products_b2b=Product.objects.filter(Q(order=week_orders_b2b)&(Q(mapped_tracking_no__isnull=True)|Q(mapped_tracking_no__exact='')))

	week_products_b2b=Product.objects.filter(Q(order=week_orders_b2b)&Q(applied_weight__isnull=True))
	
# business stats grouped by businesses


	context = {'week_shipments':week_shipments,'week_products_b2b':week_products_b2b}
	return render(request, 'polls/index1.html', context)


def results(request):
	todays_date=date.today()
	threshold_days_before=date.today()-datetime.timedelta(days=3)

# today min/max
	
#week min/max	
	date_max = datetime.datetime.combine(threshold_days_before, datetime.time.max)
	start_date = datetime.datetime(2015, 7, 10, 0, 0)

#customer stats today
	
#customer stats week
	week_orders =Order.objects.filter(Q(book_time__range=(start_date,date_max))&(Q(order_status='C')))
	late_shipments=Shipment.objects.filter(Q(order=week_orders)&Q(status='P'))


#business stats today

	
#b2b week
	late_orders_b2b =BOrder.objects.filter(Q(book_time__range=(start_date,date_max))&(Q(status='P') | Q(status='PU')| Q(status='D')))
	late_products_b2b=Product.objects.filter(Q(order=late_orders_b2b))
	context = {'late_shipments':late_shipments,'late_products_b2b':late_products_b2b}


	return render(request, 'polls/index2.html', context)



def vote(request, question_id):
	return HttpResponse("You're voting on question %s." % question_id)
