import csv
import json
import re
import textwrap

import magic
from django.core.context_processors import csrf
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from businessapp.forms import UploadFileForm
from businessapp.models import Order,Product,Business, AddressDetails
from PyPDF2 import PdfFileWriter, PdfFileReader
import cStringIO
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from datetime import date,timedelta
import datetime
from django.db.models import Avg, Count, F, Max, Min, Sum, Q, Prefetch
import inflect

from core.models import Pincode


@login_required
def print_address_view(request):
    order_no = request.GET.get("order_no", None)
    if order_no is None:
        raise ValidationError("Please provide an order_no")
    order = Order.objects.get(pk=order_no)
    return render(request, 'PrintAddress.html', {"order": order})


@login_required
def print_invoice_order_view(request):
    order_no = request.GET.get("order_no", None)

    if order_no is None:
        raise ValidationError("Please provide an order_no")
    order = Order.objects.get(pk=order_no)
    product_set=order.product_set.all()
    total=0
    total_quantity=0
    for product in product_set:
        total=total+ int(product.price)
        total_quantity=total_quantity+ int(product.quantity)
    p = inflect.engine()
    total_word=p.number_to_words(int(total))
    total_word=total_word + " Only"

    return render(request, 'invoice.html', {"order": order,"total":total,"total_word":total_word,"total_quantity":total_quantity})


@login_required
def print_invoice_product_view(request):
    order_no = request.GET.get("order_no", None)
    price = request.GET.get("price", None)
    if order_no is None:
        raise ValidationError("Please provide an order_no")
    product = Product.objects.get(pk=order_no)
    total=product.price
    total_quantity=product.quantity
    p = inflect.engine()
    total_word=p.number_to_words(int(total))
    total_word=total_word + " Only"
    if price:
        product.price=price
        total=product.price
        total_quantity=product.quantity
        p = inflect.engine()
        total_word=p.number_to_words(int(total))
        total_word=total_word + " Only"

    return render(request, 'invoice2.html', {"product": product,"total":total,"total_word":total_word,"total_quantity":total_quantity})


@login_required
def barcode_stats_view(request):

    todays_date = date.today()
    week_before = date.today() - datetime.timedelta(days=10)
    yesterdays_date=date.today() - datetime.timedelta(days=1)
    y=Order.objects.filter(Q(book_time__gt=week_before) & ( ~Q(status='P') & ~Q(status='CA')   ) ).extra({'date_created' : "date(book_time)"}).values('date_created').annotate(barcode_count=Count('product__barcode'),created_count=Count('product'))

    data = {'date': [], 'wbarcode': [], 'wobarcode': []}

    #data= Business.objects.filter(order__book_time__gt=todays_date).annotate(product_total=Count('order__product')).annotate(barcode_total=Count('product__barcode')).annotate(pickupboy='pb')

    data2=Product.objects.filter(Q(order__book_time__gt=todays_date) & ( ~Q(status='P') & ~Q(status='CA')   )).values('order__business','order__business__pb__name','order__business__warehouse__name').annotate(product_total=Count('pk')).annotate(barcode_total=Count('barcode'))

    data3=Product.objects.filter(Q(order__book_time__lt=todays_date) & Q(order__book_time__gt=yesterdays_date) & ( ~Q(status='P') & ~Q(status='CA')   )).values('order__business','order__business__pb__name','order__business__warehouse__name').annotate(product_total=Count('pk')).annotate(barcode_total=Count('barcode'))

    for x in data2:
        x['without']=x['product_total']-x['barcode_total']

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
    return render(request, 'barcode_chart.html', {"series": series,"categories": categories,"data2":data2,"data3":data3})


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


def handle_uploaded_file(f, pickup_address):
    mem_file = ContentFile(f.read())
    reader_raw = csv.DictReader(mem_file)
    reader = [row for row in reader_raw]
    result = []
    ref_fieldnames = ['receiver_name', 'receiver_phone', 'receiver_address', 'receiver_pincode', 'receiver_email',
                      'payment_method', 'reference_id', 'shipment_method', 'item_name', 'item_price', 'item_weight',
                      'item_sku', 'barcode']
    phone_check = re.compile("^\d{10}$")
    email_check = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    barcode_check = re.compile("^SE[0-9]{8}$")
    if set(ref_fieldnames) != set(reader_raw.fieldnames):
        return [{
            "error": True,
            "row": None,
            "column": None,
            "message": "Column names don't match. Please ensure the sheet uploaded is the same as the template"
        }]

    for i, row in enumerate(reader, start=2):
        if len(row['receiver_name']) < 1:
            result.append({
                "error": True,
                "row": i,
                "column": "receiver_name",
                "message": "Receiver name is a required field"
            })
        if not re.match(phone_check, row['receiver_phone']):
            result.append({
                "error": True,
                "row": i,
                "column": "receiver_phone",
                "message": "Receiver phone should be 10 digits"
            })
        if len(row["receiver_address"]) > 120 or len(row["receiver_address"]) < 1:
            result.append({
                "error": True,
                "row": i,
                "column": "receiver_address",
                "message": "Receiver address should be 1-120 characters"
            })
        r_pincodes = Pincode.objects.filter(pincode=row['receiver_pincode'])
        r_pincode = None
        if r_pincodes.count() < 1:
            result.append({
                "error": True,
                "row": i,
                "column": "receiver_pincode",
                "message": "Enter a valid pincode"
            })
        else:
            r_pincode = r_pincodes.first()
            if r_pincode.district_name is None or r_pincode.state_name is None:
                result.append({
                    "error": True,
                    "row": i,
                    "column": "receiver_pincode",
                    "message": "Enter a valid pincode"
                })
        if row['receiver_email']:
            if not re.match(email_check, row['receiver_email']):
                result.append({
                    "error": True,
                    "row": i,
                    "column": "receiver_email",
                    "message": "Not a valid email address"
                })
        if not row['payment_method'].upper() in ['F', 'C']:
            result.append({
                "error": True,
                "row": i,
                "column": "payment_method",
                "message": "Enter a valid payment method. F -> Free Shipping, C -> COD"
            })
        if row['payment_method'].upper() == 'C' and r_pincode:
            if not (r_pincode.fedex_cod_service and not r_pincode.fedex_oda_opa):
                if not r_pincode.ecom_servicable:
                    result.append({
                        "error": True,
                        "row": i,
                        "column": "payment_method",
                        "message": "COD Service not available at this pincode"
                    })
        if len(row['reference_id']) > 100:
            result.append({
                "error": True,
                "row": i,
                "column": "reference_id",
                "message": "Max length for reference_id is 100"
            })
        if not row['shipment_method'].upper() in ['B', 'N']:
            result.append({
                "error": True,
                "row": i,
                "column": "shipment_method",
                "message": "Enter a valid shipping method. B -> Bulk, N -> Premium"
            })
        if len(row['item_name']) < 1:
            result.append({
                "error": True,
                "row": i,
                "column": "item_name",
                "message": "item_name is a required field"
            })
        try:
            float(row['item_price'])
        except ValueError:
            result.append({
                "error": True,
                "row": i,
                "column": "item_price",
                "message": "item_price is a required field and should be a valid float value"
            })
        try:
            float(row['item_weight'])
        except ValueError:
            result.append({
                "error": True,
                "row": i,
                "column": "item_weight",
                "message": "item_weight is a required field and should be a valid float value"
            })

        if row['item_sku']:
            if len(row['item_sku']) > 100:
                result.append({
                    "error": True,
                    "row": i,
                    "column": "item_sku",
                    "message": "item_sku should be <= 100 characters"
                })

        if row['barcode']:
            if not re.match(barcode_check, row['barcode']):
                result.append({
                    "error": True,
                    "row": i,
                    "column": "barcode",
                    "message": "Enter a valid barcode. SE**********"
                })
            duplicate_entries = []
            for j, rw in enumerate(reader, start=2):
                if i != j:
                    if rw['barcode'] == row['barcode']:
                        duplicate_entries.append(j)
            if len(duplicate_entries) > 0:
                result.append({
                    "error": True,
                    "row": i,
                    "column": "barcode",
                    "message": "Duplicate barcode entries in rows: {}".format(str(duplicate_entries))
                })
            try:
                Product.objects.get(barcode=row['barcode'])
                result.append({
                    "error": True,
                    "row": i,
                    "column": "barcode",
                    "message": "Barcode already exists. Duplicate entry"
                })
            except ObjectDoesNotExist:
                pass

    if len(result) > 0:
        return result
    else:
        orders_created = []
        products_created = []
        for r in reader:
            address = textwrap.wrap(text=str(r['receiver_address']), width=60)
            address1 = address[0]
            address2 = address[1] if len(address) > 1 else None
            r_pincodes = Pincode.objects.filter(pincode=r['receiver_pincode'])
            r_pincode = r_pincodes.first()
            order = Order(
                name=r['receiver_name'],
                phone=r['receiver_phone'],
                address1=address1,
                address2=address2,
                city=r_pincode.district_name,
                state=r_pincode.state_name,
                pincode=r['receiver_pincode'],
                country='India',
                payment_method=r['payment_method'].upper(),
                method=r['shipment_method'].upper(),
                business=pickup_address.business,
                pickup_address=pickup_address,
                reference_id=r['reference_id'],
                email=r['receiver_email']
            )
            try:
                order.save()
                orders_created.append(order)
            except Exception as e:
                for o in orders_created:
                    o.delete()
                for p in products_created:
                    p.delete()
                return [{
                    "error": True,
                    "r": None,
                    "column": None,
                    "message": "Unknown error. Please contact your BDM with this message: " + str(e)
                }]
            product = Product(
                name=r['item_name'],
                price=r['item_price'],
                weight=r['item_weight'],
                sku=r['item_sku'],
                barcode=r['barcode'] if r['barcode'] != '' else None,
                order=order
            )
            try:
                product.save()
                products_created.append(product)
            except Exception as e:
                for o in orders_created:
                    o.delete()
                for p in products_created:
                    p.delete()
                return [{
                    "error": True,
                    "r": None,
                    "column": None,
                    "message": "Unknown error. Please contact your BDM with this message: " + str(e)
                }]
        return [{
            "error": False,
            "row": None,
            "column": None,
            "message": "{} orders created".format(len(orders_created))
        }]


@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        pickup_address_id = request.POST.get('pid', None)
        if pickup_address_id is None:
            return HttpResponse(json.dumps({"result": [{
                "error": True,
                "row": None,
                "column": None,
                "message": "No pickup_address (pid) provided."
            }]}), content_type='application/json', status=400)
        try:
            pickup_address = AddressDetails.objects.get(pk=pickup_address_id)
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps({"result": [{
                "error": True,
                "row": None,
                "column": None,
                "message": "pickup_address (pid) not found. Please enter a valid pid"
            }]}), content_type='application/json', status=400)
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES['file']:
                result = handle_uploaded_file(request.FILES['file'], pickup_address)
                return HttpResponse(json.dumps({"result": result}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({"result": [{
                "error": True,
                "row": None,
                "column": None,
                "message": "Invalid file. Please upload a valid csv file."
            }]}), content_type='application/json', status=400)
    else:
        return HttpResponseNotAllowed(['POST'])

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

    warning_products=total_products.filter(warning_type__isnull=False)
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
