from django.core.exceptions import ValidationError
from django.shortcuts import render
from businessapp.models import Order
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
    return render(request, 'barcode_chart.html', {"series": series,"categories": categories})


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