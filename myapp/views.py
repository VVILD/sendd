from django.shortcuts import render

from myapp.models import *
# Create your views here.
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch
from businessapp.models import Order as BOrder
from businessapp.models import Product,Business
import json
from django.http import HttpResponse

from myapp.forms import NewShipmentForm
from django.views.generic.edit import FormView

import datetime
from datetime import date
import datetime
from django.db.models import Avg
from pprint import pprint
from itertools import groupby

def index(request):
	todays_date=date.today()
	week_before=date.today()-datetime.timedelta(days=62)

# today min/max
	today_min = datetime.datetime.combine(todays_date, datetime.time.min)
	today_max = datetime.datetime.combine(todays_date, datetime.time.max)
	
#week min/max	
	date_min = datetime.datetime.combine(week_before, datetime.time.min)
	date_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
	
#customer stats today


	today_orders =Order.objects.filter(Q(book_time__range=(today_min,today_max))&(Q(status='P') | Q(status='C')| Q(status='DI')))
	today_shipments_correct=Shipment.objects.filter(order=today_orders).exclude(price__isnull=True).exclude(price__exact='')
	today_shipments=Shipment.objects.filter(order=today_orders)
	average_b2c=today_shipments_correct.aggregate(Avg('price'))['price__avg']
	sum_b2c=today_shipments_correct.aggregate(Sum('price'))['price__sum']
	count_b2c=today_shipments_correct.count()
	action_b2c=today_shipments.count()-today_shipments_correct.count()
	
#customer stats week
	week_orders =Order.objects.filter(Q(book_time__range=(date_min,date_max))&(Q(status='P') | Q(status='C')| Q(status='C')))
	week_shipments=Shipment.objects.filter(order=week_orders).values('order__book_time','price').exclude(price__isnull=True).exclude(price__exact='')

	b2c_stats=[]
	for key, values in groupby(week_shipments, key=lambda row: row['order__book_time'].date()):
	    print('-')
	    #pprint(key)
	    x=list(values)
	    print len(x)
	    sum=0
	    for y in x:
	        sum=sum+float(y['price'])
	    print sum
	    b2c_stats.append([str(key),len(x),sum,sum/len(x)])

#business stats today
	today_orders_b2b=BOrder.objects.filter(Q(book_time__range=(today_min,today_max))&(Q(status='P') | Q(status='C')| Q(status='DI')| Q(status='D')))
	today_products_correct=Product.objects.filter(order=today_orders_b2b).exclude(shipping_cost__isnull=True)
	today_products=Product.objects.filter(order=today_orders_b2b)
	average_b2b=today_products_correct.aggregate(total=Avg('shipping_cost', field="shipping_cost+cod_cost"))['total']
	sum_b2b=today_products_correct.aggregate(total=Sum('shipping_cost', field="shipping_cost+cod_cost"))['total']
	count_b2b=today_products_correct.count()
	action_b2b=today_products.count()-today_products_correct.count()

	
#b2b week
	week_orders_b2b =BOrder.objects.filter(Q(book_time__range=(date_min,date_max))&(Q(status='P') | Q(status='C')| Q(status='D')| Q(status='DI')))
	week_products_b2b=Product.objects.filter(order=week_orders_b2b).values('order__book_time','shipping_cost','cod_cost').exclude(shipping_cost__isnull=True)
	
	week_products_b2b=Product.objects.filter(order=week_orders_b2b).values('order__book_time','shipping_cost','cod_cost').exclude(shipping_cost__isnull=True)

	product=Product.objects.extra(select={'day': 'date( date)'}).values('day').annotate(count=Count('pk'),shipping_sum=Sum('shipping_cost'),cod_sum=Sum('cod_cost'),return_sum=Sum('return_cost'))

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


	context = {'product_groupedby_business':product_groupedby_business,'average_b2c':average_b2c,'sum_b2c':sum_b2c,'count_b2c':count_b2c,'average_b2b':average_b2b,'sum_b2b':sum_b2b,'count_b2b':count_b2b,'b2c_stats':b2c_stats,'b2b_stats':b2b_stats,'action_b2b':action_b2b,'action_b2c':action_b2c,'product':product}
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

	
# business stats grouped by businesses


	context = {'week_shipments':week_shipments,'week_products_b2b':week_products_b2b}
	return render(request, 'polls/index1.html', context)


def results(request):
	todays_date=date.today()
	threshold_days_before=date.today()-datetime.timedelta(days=2)

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
	holachef=Business.objects.get(pk='holachef')
	late_orders_b2b =BOrder.objects.filter(Q(book_time__range=(start_date,date_max))&(Q(status='P') | Q(status='PU')| Q(status='D'))).exclude(business=holachef)
	late_products_b2b=Product.objects.filter(Q(order=late_orders_b2b))

	for product in late_products_b2b:

		product.latest_status=json.loads(product.tracking_data)[-1]['status']

		

	context = {'late_shipments':late_shipments,'late_products_b2b':late_products_b2b}


	return render(request, 'polls/index2.html', context)



def vote(request):
	
	#for july

#if pincode 400 then mumbai else ROI
#all revenue in base rate u have to add ++
#rates are 20,40,8,12
#orders without applied weight not counted orders without method not counted,without pincode not counted
	start_date = datetime.datetime(2015, 8, 10)
	results=[]
	for num in range(0,10):
		week_start_date=start_date+ datetime.timedelta(days=7*num)
		row=[]
		row.append(week_start_date)
		start_date=datetime.datetime.combine(row[0], datetime.time.min)
		end_date=row[0]+datetime.timedelta(days=6)
		end_date=datetime.datetime.combine(end_date, datetime.time.max)


		week_orders_b2b =BOrder.objects.filter(Q(book_time__range=(start_date,end_date)))
		week_products_b2b=Product.objects.filter(Q(order=week_orders_b2b)&(Q(applied_weight__isnull=False)))

		sum_weight=[0,0,0,0]
		sum_revenue=[0,0,0,0]
		count=[0,0,0,0]
		rates=[20,40,8,12]
		try:
			for x in week_products_b2b:
				weight= round(x.applied_weight * 2) / 2
				if x.order.pincode[:3]=='400':
					if x.order.method=='N':
						key=0
					else:
						key=2
				else:
					if x.order.method=='N':
						key=1
					else:
						key=3

				sum_weight[key]=sum_weight[key]+weight
				sum_revenue[key]=sum_revenue[key]+weight*2*rates[key] 
				count[key]=count[key]+1
		except:
			pass

		row.append(sum_weight)
		row.append(sum_revenue)
		row.append(count)
		results.append(row)

	context = {'results':results}

	return render(request, 'polls/index3.html', context)


class NewShipmentView(FormView):

	template_name='newshipment.html'
	form_class=NewShipmentForm

	def form_valid(self, form):

		return super(NewShipmentView, self).form_valid(form)


from django.shortcuts import render
from django.http import HttpResponseRedirect


def get_name(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewShipmentForm(request.POST)
        print "hi"
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print "hi2"
        
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    elif request.method=='GET':
        print "hi3"
        
        form = NewShipmentForm()

    return render(request, 'newshipment.html', {'form': form})
