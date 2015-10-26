from django.core.exceptions import ValidationError
from django.shortcuts import render
from businessapp.models import Order,Product,Business
from PyPDF2 import PdfFileWriter, PdfFileReader
import cStringIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import date,timedelta
import datetime
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch

@login_required
def print_address_view(request):
    order_no = request.GET.get("order_no", None)
    if order_no is None:
        raise ValidationError("Please provide an order_no")
    order = Order.objects.get(pk=order_no)
    return render(request, 'PrintAddress.html', {"order": order})


@login_required
def barcode_stats_view(request):

    todays_date = date.today()
    week_before = date.today() - datetime.timedelta(days=10)
    y=Order.objects.filter(Q(book_time__gt=week_before) & ( ~Q(status='P') & ~Q(status='CA')   ) ).extra({'date_created' : "date(book_time)"}).values('date_created').annotate(barcode_count=Count('product__barcode'),created_count=Count('product'))

    data = {'date': [], 'wbarcode': [], 'wobarcode': []}

    data= Business.objects.filter(order__book_time__gt=todays_date).annotate(product_total=Count('order__product')).annotate(barcode_total=Count('product__barcode')).annotate(pickupboy='pb')

    data2=Product.objects.filter(Q(order__book_time__gt=todays_date) & ( ~Q(status='P') & ~Q(status='CA')   )).values('order__business','order__business__pb__name').annotate(product_total=Count('pk')).annotate(barcode_total=Count('barcode'))



    for x in y:
        data['date'].append(str(x["date_created"]))
        data['wbarcode'].append((x["barcode_count"]))
        data['wobarcode'].append((x["created_count"]-x["barcode_count"]))

    categories=data['date']

    series=[{
            "name": 'without barcode',
            "data": data['wobarcode']
        }, {
            "name": 'with barcode',
            "data": data['wbarcode']
        }]
    return render(request, 'barcode_chart.html', {"series": series,"categories": categories,"data2":data2})


import os

@login_required
def readpdf(request):
    print os.path.dirname(os.path.realpath(__file__))
    input1 = PdfFileReader(open("/home/django/django_project/ffmanual.pdf", "rb"))
    output =PdfFileWriter()

    for i in range(0, input1.getNumPages()-1):
        output.addPage(input1.getPage(i))

    outputStream = cStringIO.StringIO()
    output.write(outputStream)

    response = HttpResponse(content_type='application/pdf')
#	response['Content-Disposition'] = 'attachment; filename="Manual_version1.0.pdf"'
    response.write(outputStream.getvalue())

    return response


@login_required
def qc_stats_view(request):


    date_old=request.GET['date']
    todays_date = date.today()
    threshold_before = date.today() - datetime.timedelta(days=int(date_old))

    total_products=Product.objects.filter(Q(order__book_time__lt=threshold_before)&Q(order__status='DI')).exclude(Q(status='C')|Q(return_action='R')|Q(return_action='RB')).exclude(order__business='ecell').exclude(order__business='ghasitaram').exclude(order__business='holachef')



    total_products_count=total_products.count()
    total_products_data=total_products.extra(select={'name': 'company'}).values('name').annotate(y=Count('company'))

    baap=total_products.values('company').annotate(total=Count('company')).annotate(withwarning=Count('warning_type')).annotate(withcomment=Count('qc_comment')).annotate(withfollowup=Count('follow_up'))

    for x in total_products_data:
        x['name']=str(x['name'])

    warning_products=total_products.filter(warning_type__isnull=True)
    warning_products_count=warning_products.count()
    warning_products_data=warning_products.extra(select={'name': 'company'}).values('name').annotate(y=Count('company'))
    for x in warning_products_data:
        x['name']=str(x['name'])


    comment_products=total_products.filter(qc_comment__isnull=False)
    comment_products_count=comment_products.count()
    comment_products_data=comment_products.extra(select={'name': 'company'}).values('name').annotate(y=Count('company'))

    for x in comment_products_data:
        x['name']=str(x['name'])


    noncomment_products=total_products.filter(qc_comment__isnull=True)
    noncomment_products_count=noncomment_products.count()
    noncomment_products_data=noncomment_products.extra(select={'name': 'company'}).values('name').annotate(y=Count('company'))

    for x in noncomment_products_data:
        x['name']=str(x['name'])

    print ""
    nofollowup_products=total_products.filter(follow_up__isnull=False)
    nofollowup_products_count=nofollowup_products.count()
    nofollowup_products_data=nofollowup_products.extra(select={'name': 'company'}).values('name').annotate(y=Count('company'))

    for x in nofollowup_products_data:
        x['name']=str(x['name'])

    un_count=Product.objects.filter(Q(order__book_time__lt=threshold_before) & Q(order__book_time__gt=datetime.date(2015, 9, 1)) & (Q(order__status__in=['PU','D'])) &(Q(mapped_tracking_no__isnull=True) | Q(mapped_tracking_no__exact=""))).count()

    return render(request, 'qc_stat.html', {"nofollowup_products_count": nofollowup_products_count,"nofollowup_products_data": nofollowup_products_data,"warning_products_count": warning_products_count,"warning_products_data": warning_products_data,"total_products_count": total_products_count,"total_products_data": total_products_data,"comment_products_count": comment_products_count,"comment_products_data": comment_products_data,"noncomment_products_count": noncomment_products_count,"noncomment_products_data": noncomment_products_data,"date":date_old,"baap":baap,"un_count":un_count})
