import json
import io
import string
from datetime import datetime, timedelta
from pytz import timezone
from xlsxwriter.workbook import Workbook
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import cStringIO
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
import base64
from businessapp.models import Product
from businessapp.models import Order as BusinessOrder
from core.models import EcomAWB
from core.utils.fedex_legacy_helper import FedexLegacy
from myapp.models import Order as CustomerOrder
import core.utils.fedex_api_helper as fedex
from myapp.models import Shipment
from django.core.exceptions import ObjectDoesNotExist

__author__ = 'vatsalshah'


@login_required()
def create_fedex_shipment(request):
    order_pk = request.GET.get('order_pk', None)
    client_type = request.GET.get('client_type', None)

    return render(request, 'fedex_new_shipment.html', fedex_view_util(order_pk, client_type))


def fedex_view_util(order_pk, client_type):
    data = []
    master_tracking_no = None
    shipping_cost = None
    fedex_ship_docs_url = None
    output = PdfFileWriter()
    if client_type == 'business':
        products = Product.objects.filter(order__pk=order_pk).select_related('order')
        package_count = products.count()
        items = [{
                     "name": p.name,
                     "weight": p.applied_weight,
                     "price": p.price,
                     "quantity": p.quantity,
                     "is_doc": p.is_document
                 } for p in products]
        total_docs = sum(i['is_doc'] for i in items)
        total_weight = sum(i['weight'] for i in items)
        total_price = sum(i['price'] for i in items)
        is_cod = False
        if products[0].order.payment_method == 'C':
            is_cod = True
        service_type, config = fedex.get_service_type(str(products[0].order.method), total_price,
                                                      total_weight, products[0].order.city, products[0].order.pincode, is_cod)
        for idx, product in enumerate(products, start=1):
            sender_details = None
            warehouse = None
            receiver_warehouse = None
            receiver_name = product.order.name
            receiver_company = None
            receiver_phone = product.order.phone
            receiver_address1 = str(product.order.address1)
            receiver_address2 = str(getattr(product.order, 'address2', ''))
            receiver_address = receiver_address1 + receiver_address2
            receiver_city = product.order.city
            receiver_state = product.order.state
            receiver_pincode = product.order.pincode
            receiver_country_code = 'IN'
            is_business_receiver = False
            product_type = product.order.payment_method
            is_cod = False
            if product.order.pickup_address is not None:
                sender_details = product.order.pickup_address.__dict__
            if product.order.pickup_address.warehouse is not None:
                warehouse = product.order.pickup_address.warehouse.__dict__
            if product.order.is_reverse:
                previous_order = BusinessOrder.objects.get(pk=product.order.reference_id)
                receiver_warehouse = previous_order.pickup_address.warehouse.__dict__
            if product_type == 'C':
                is_cod = True
            sender = {
                "is_cod": is_cod,
                "sender_details": sender_details,
                "warehouse": warehouse
            }
            receiver = {
                "name": receiver_name,
                "company": receiver_company,
                "phone": receiver_phone,
                "address": receiver_address,
                "city": receiver_city,
                "state": receiver_state,
                "pincode": receiver_pincode,
                "is_business": is_business_receiver,
                "country_code": receiver_country_code,
                "warehouse": receiver_warehouse
            }
            if idx == 1:
                item = items
            else:
                item = [{
                    "name": product.name,
                    "weight": product.applied_weight,
                    "price": product.price,
                    "quantity": product.quantity,
                    "is_doc": product.is_document
                }]
            result = fedex.create_shipment(sender, receiver, item, config, service_type, idx, package_count,
                                           master_tracking_no, product.order.is_reverse)
            if result['status'] != 'ERROR':
                if product.mapped_tracking_no:
                    product.tracking_history = str(product.tracking_history) + ',' + str(product.mapped_tracking_no)
                product.mapped_tracking_no = result['tracking_number']
                if idx == 1:
                    master_tracking_no = result['tracking_number']

                f1 = ContentFile(base64.b64decode(result['OUTBOUND_LABEL']))
                input1 = PdfFileReader(f1, strict=False)
                output.addPage(input1.getPage(0))
                if total_docs != package_count or is_cod:
                    output.addPage(input1.getPage(1))
                    output.addPage(input1.getPage(2))

                if is_cod and result['COD_RETURN_LABEL'] is not None:
                    f2 = ContentFile(base64.b64decode(result['COD_RETURN_LABEL']))
                    input2 = PdfFileReader(f2, strict=False)
                    output.addPage(input2.getPage(0))
                    if total_docs != package_count or is_cod:
                        output.addPage(input2.getPage(1))

                if result['COMMERCIAL_INVOICE'] is not None and (total_docs != package_count or is_cod):
                    f3 = ContentFile(base64.b64decode(result['COMMERCIAL_INVOICE']))
                    input3 = PdfFileReader(f3, strict=False)
                    output.addPage(input3.getPage(0))
                    output.addPage(input3.getPage(0))
                    output.addPage(input3.getPage(0))
                    if products[0].order.method == 'B' or service_type == "FEDEX_EXPRESS_SAVER":
                        output.addPage(input3.getPage(0))

                if result["shipping_cost"]:
                    shipping_cost = float(result["shipping_cost"])
                product.company = 'F'
                product.save()

                data.append({
                    "shipment_no": idx,
                    "shipment_name": product.name,
                    "status": result['status'],
                    "tracking_number": result["tracking_number"],
                    "is_cod": is_cod,
                    "service_type": result["service_type"],
                    "account": result["account"]
                })
        output.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
        outputStream = cStringIO.StringIO()
        output.write(outputStream)
        order = BusinessOrder.objects.get(pk=order_pk)
        order.fedex_ship_docs.save(master_tracking_no + '.pdf', ContentFile(outputStream.getvalue()))
        order.mapped_master_tracking_number = master_tracking_no
        order.save()
        fedex_ship_docs_url = str(order.fedex_ship_docs.name).split('/')[-1]

    elif client_type == 'customer':
        shipments = Shipment.objects.filter(order__pk=order_pk).select_related('order')
        package_count = shipments.count()
        for idx, shipment in enumerate(shipments, start=1):
            sender_details = None
            warehouse = None
            item_name = shipment.item_name
            item_weight = shipment.weight
            if shipment.order.warehouse is not None:
                warehouse = shipment.order.warehouse.__dict__
            if shipment.order.namemail.name is not None:
                sender_details = {"business_name": shipment.order.namemail.name}
            receiver_name = shipment.drop_name
            receiver_company = None
            receiver_phone = shipment.drop_phone
            receiver_address = shipment.drop_address.flat_no + shipment.drop_address.locality
            receiver_city = shipment.drop_address.city
            receiver_state = shipment.drop_address.state
            receiver_pincode = shipment.drop_address.pincode
            receiver_country_code = 'IN'
            is_business_receiver = False
            service_type, config = fedex.get_service_type(str(shipment.category), float(shipment.cost_of_courier),
                                                          float(item_weight), receiver_city, receiver_pincode)
            item_price = shipment.cost_of_courier
            sender = {
                "is_cod": False,
                "sender_details": sender_details,
                "warehouse": warehouse
            }
            receiver = {
                "name": receiver_name,
                "company": receiver_company,
                "phone": receiver_phone,
                "address": receiver_address,
                "city": receiver_city,
                "state": receiver_state,
                "pincode": receiver_pincode,
                "is_business": is_business_receiver,
                "country_code": receiver_country_code
            }
            if idx == 1:
                item = [{
                            "name": s.item_name,
                            "weight": s.weight,
                            "price": s.cost_of_courier
                        } for s in shipments]
            else:
                item = [{
                    "name": shipment.item_name,
                    "weight": shipment.weight,
                    "price": shipment.cost_of_courier
                }]

            result = fedex.create_shipment(sender, receiver, item, config, service_type, idx, package_count,
                                           master_tracking_no, False)
            if result['status'] != 'ERROR':

                if shipment.mapped_tracking_no:
                    shipment.tracking_history = str(shipment.tracking_history) + ',' + str(shipment.mapped_tracking_no)
                shipment.mapped_tracking_no = result['tracking_number']
                if idx == 1:
                    master_tracking_no = result['tracking_number']

                f1 = ContentFile(base64.b64decode(result['OUTBOUND_LABEL']))
                input1 = PdfFileReader(f1, strict=False)
                output.addPage(input1.getPage(0))
                output.addPage(input1.getPage(1))
                output.addPage(input1.getPage(2))

                if result['COMMERCIAL_INVOICE'] is not None:
                    f3 = ContentFile(base64.b64decode(result['COMMERCIAL_INVOICE']))
                    input3 = PdfFileReader(f3, strict=False)
                    output.addPage(input3.getPage(0))

                if result["shipping_cost"]:
                    shipping_cost = float(result["shipping_cost"])
                shipment.status = 'DI'
                shipment.company = 'F'

                shipment.save()

                data.append({
                    "shipment_no": idx,
                    "shipment_name": item_name,
                    "status": result['status'],
                    "tracking_number": result["tracking_number"],
                    "is_cod": False,
                    "service_type": result["service_type"],
                    "account": result["account"]
                })
        order = CustomerOrder.objects.get(pk=order_pk)
        output.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
        outputStream = cStringIO.StringIO()
        output.write(outputStream)
        order.fedex_ship_docs.save(master_tracking_no + '.pdf', ContentFile(outputStream.getvalue()))
        fedex_ship_docs_url = str(order.fedex_ship_docs.name).split('/')[-1]
        order.mapped_master_tracking_number = master_tracking_no
        order.save()
    return {
        "data": data,
        "shipping_cost": shipping_cost,
        "fedex_ship_docs_url": fedex_ship_docs_url
    }


@login_required()
def barcode_fedex_redirector(request, barcode):
    try:
        shipment = Shipment.objects.get(barcode=barcode)
    except ObjectDoesNotExist:
        try:
            shipment = Product.objects.get(barcode=barcode)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest("Barcode doesn't exist")

    if shipment.barcode is None:
        return HttpResponseBadRequest("Fedex order not created yet")
    if shipment.fedex_outbound_label is None:
        return HttpResponseBadRequest("Fedex order not created yet")
    static_url = 'http://sendmates.com/static/'
    labels = [static_url + str(shipment.fedex_outbound_label.name).split('/')[-1]]
    if shipment.fedex_cod_return_label is not None:
        labels.append(static_url + str(shipment.fedex_cod_return_label.name).split('/')[-1])
    return render(request, 'fedex_print.html', {"urlList": labels})


@login_required()
def create_individual_fedex_shipment(request):
    shipment_pk = request.GET.get('shipment_pk', None)
    client_type = request.GET.get('client_type', None)
    sender_details = None
    warehouse = None
    receiver_name = None
    receiver_phone = None
    receiver_company = None
    receiver_address = None
    receiver_city = None
    receiver_state = None
    receiver_pincode = None
    receiver_country_code = None
    is_business_receiver = None
    item_name = None
    item_weight = None
    service_type = None
    item_price = None
    fedex_legacy = FedexLegacy()
    is_cod = False
    config = None
    if client_type == 'business':
        product = Product.objects.get(pk=shipment_pk)
        item_name = product.name
        item_weight = product.applied_weight
        receiver_name = product.order.name
        receiver_company = None
        receiver_phone = product.order.phone
        receiver_address1 = product.order.address1
        receiver_address2 = product.order.address2
        receiver_address = receiver_address1 + receiver_address2
        receiver_city = product.order.city
        receiver_state = product.order.state
        receiver_pincode = product.order.pincode
        receiver_country_code = 'IN'
        is_business_receiver = False
        product_type = product.order.payment_method
        is_cod = False
        if product.order.business.business_name is not None:
            sender_details = product.order.business.__dict__
        if product.order.business.warehouse is not None:
            warehouse = product.order.business.warehouse.__dict__
        if product_type == 'C':
            is_cod = True
        service_type, config = fedex_legacy.get_service_type(str(product.order.method), float(product.price),
                                                             float(item_weight), receiver_city, is_cod)
        item_price = product.price
    elif client_type == 'customer':
        shipment = Shipment.objects.get(pk=shipment_pk)
        item_name = shipment.item_name
        item_weight = shipment.weight
        if shipment.order.warehouse is not None:
            warehouse = shipment.order.warehouse.__dict__
        if shipment.order.namemail.name is not None:
            sender_details = {"business_name": shipment.order.namemail.name}
        receiver_name = shipment.drop_name
        receiver_company = None
        receiver_phone = shipment.drop_phone
        receiver_address = shipment.drop_address.flat_no + shipment.drop_address.locality
        receiver_city = shipment.drop_address.city
        receiver_state = shipment.drop_address.state
        receiver_pincode = shipment.drop_address.pincode
        receiver_country_code = 'IN'
        is_business_receiver = False
        service_type, config = fedex_legacy.get_service_type(str(shipment.category), float(shipment.cost_of_courier),
                                                             float(item_weight), receiver_city)
        item_price = shipment.cost_of_courier

    sender = {
        "is_cod": is_cod,
        "sender_details": sender_details,
        "warehouse": warehouse
    }
    receiver = {
        "name": receiver_name,
        "company": receiver_company,
        "phone": receiver_phone,
        "address": receiver_address,
        "city": receiver_city,
        "state": receiver_state,
        "pincode": receiver_pincode,
        "is_business": is_business_receiver,
        "country_code": receiver_country_code
    }
    item = {
        "name": item_name,
        "weight": item_weight,
        "price": item_price
    }
    result = fedex_legacy.create_shipment(sender, receiver, item, config, service_type)
    fedex_ship_docs_url = None
    if result['status'] != 'ERROR':
        if client_type == 'business':
            if product.mapped_tracking_no:
                product.tracking_history = str(product.tracking_history) + ',' + str(product.mapped_tracking_no)
            product.mapped_tracking_no = result['tracking_number']

            output = PdfFileWriter()
            f1 = ContentFile(base64.b64decode(result['OUTBOUND_LABEL']))
            input1 = PdfFileReader(f1, strict=False)
            output.addPage(input1.getPage(0))
            output.addPage(input1.getPage(1))
            output.addPage(input1.getPage(2))

            if is_cod:
                f2 = ContentFile(base64.b64decode(result['COD_RETURN_LABEL']))
                input2 = PdfFileReader(f2, strict=False)
                output.addPage(input2.getPage(0))
                output.addPage(input2.getPage(1))

            f3 = ContentFile(base64.b64decode(result['COMMERCIAL_INVOICE']))
            input3 = PdfFileReader(f3, strict=False)
            output.addPage(input3.getPage(0))

            output.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
            outputStream = cStringIO.StringIO()
            output.write(outputStream)
            product.fedex_ship_docs.save(result['tracking_number'] + '.pdf',
                                         ContentFile(outputStream.getvalue()))
            fedex_ship_docs_url = str(product.fedex_ship_docs.name).split('/')[-1]
            if result["shipping_cost"]:
                product.actual_shipping_cost = float(result["shipping_cost"])
            product.company = 'F'
            product.save()
        elif client_type == 'customer':
            if shipment.mapped_tracking_no:
                shipment.tracking_history = str(shipment.tracking_history) + ',' + str(shipment.mapped_tracking_no)
            shipment.mapped_tracking_no = result['tracking_number']

            output = PdfFileWriter()
            f1 = ContentFile(base64.b64decode(result['OUTBOUND_LABEL']))
            input1 = PdfFileReader(f1, strict=False)
            output.addPage(input1.getPage(0))
            output.addPage(input1.getPage(1))
            output.addPage(input1.getPage(2))

            f3 = ContentFile(base64.b64decode(result['COMMERCIAL_INVOICE']))
            input3 = PdfFileReader(f3, strict=False)
            output.addPage(input3.getPage(0))

            output.addJS("this.print({bUI:true,bSilent:false,bShrinkToFit:true});")
            outputStream = cStringIO.StringIO()
            output.write(outputStream)
            shipment.fedex_ship_docs.save(result['tracking_number'] + '.pdf',
                                          ContentFile(outputStream.getvalue()))
            fedex_ship_docs_url = str(shipment.fedex_ship_docs.name).split('/')[-1]
            if result["shipping_cost"]:
                shipment.actual_shipping_cost = float(result["shipping_cost"])
            shipment.status = 'DI'
            shipment.company = 'F'

            shipment.save()
    context = {
        "status": result['status'],
        "tracking_number": result["tracking_number"],
        "fedex_ship_docs_url": fedex_ship_docs_url,
        "is_cod": is_cod,
        "service_type": result["service_type"],
        "account": result["account"],
        "shipping_cost": result["shipping_cost"]
    }
    return render(request, 'fedex_legacy_shipment.html', {"result": context})


# @login_required()
def schedule_reverse_pickup(request):
    order_no = request.GET.get('order_no', None)
    ready_timestamp = request.GET.get('ready_timestamp', None)
    business_closetime = request.GET.get('business_closetime', None)

    print ready_timestamp

    if not (order_no and ready_timestamp and business_closetime):
        return HttpResponseBadRequest("Please provide all three parameters")

    try:
        order = BusinessOrder.objects.get(pk=order_no)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Order not found. Please check the order no")

    result = json.dumps(fedex.pickup_scheduler(order, ready_timestamp, business_closetime))

    conf_id=json.loads(result)
    conf_id=conf_id["pickup_confirmation_number"]
    print conf_id
    order.reverse_confirmation_id=conf_id
    order.save()

    return HttpResponse(result, content_type='application/json')



def create_ecom_shipment(request):
    shipment_pk = request.GET.get('shipment_pk', None)
    client_type = request.GET.get('client_type', None)
    action_type = request.GET.get('type', None)

    if client_type == 'business':
        product = Product.objects.get(pk=shipment_pk)
        if action_type == "create":
            is_cod = False
            if product.order.payment_method == 'C':
                is_cod = True
            if is_cod:
                awb = EcomAWB.objects.filter(label_type='C', used=False)
                if awb.count() == 0:
                    return HttpResponseBadRequest("Ran out of ecom cod awb. Contact tech-support@sendd.co")
            else:
                awb = EcomAWB.objects.filter(label_type='P', used=False)
                if awb.count() == 0:
                    return HttpResponseBadRequest("Ran out of ecom prepaid awb. Contact tech-support@sendd.co")
            selected_awb = awb.first()
            product.mapped_tracking_no = selected_awb.awb
            product.company = 'E'
            product.save()
            selected_awb.used = True
            selected_awb.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if action_type == 'invoice':
            return render(request, 'ecom_invoice.html', {"product": product})

        if action_type == 'label':
            return render(request, 'ecom_label.html', {"product": product})

        return HttpResponseBadRequest("Can't recognize the request type")

    else:
        return HttpResponseBadRequest("Can't recognize the request type")


LETTERS = string.uppercase


def excel_style(row, col):
    """ Convert given row and column number to an Excel-style cell name. """
    result = []
    while col:
        col, rem = divmod(col - 1, 26)
        result[:0] = LETTERS[rem]
    return ''.join(result) + str(row)


def download_ecom_orders(request):
    date = request.GET.get('date', None)
    if date is None:
        return HttpResponseBadRequest("Please provide a valid date")

    output = io.BytesIO()
    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})

    column_titles = ["Air Waybill number", "Order Number", "Product", "Shipper", "Consignee", "Consignee Address1",
                     "Consignee Address2", "Consignee Address3", "Destination City", "Pincode", "State", "Mobile",
                     "Telephone", "Item Description", "Pieces", "Collectable Value", "Declared value",
                     "Actual Weight(g)", "Volumetric Weight(g)", "Length(cms)", "Breadth(cms)", "Height(cms)",
                     "Sub Customer ID", "Pickup name", "Pickup Address", "Pickup Phone", "Pickup Pincode",
                     "Return name", "Return Address", "Return Phone", "Return Pincode"]

    for i, column_title in enumerate(column_titles, 1):
        cell = excel_style(1, i)
        worksheet.write(cell, column_title, bold)

    start_date = datetime.strptime(str(date), "%d-%m-%Y")
    end_date = datetime.strptime(str(date), "%d-%m-%Y") + timedelta(days=1)

    products = Product.objects.filter(status='DI', company='E', mapped_tracking_no__isnull=False,
                                      dispatch_time__gt=start_date, dispatch_time__lt=end_date).select_related('order')

    for i, product in enumerate(products, 2):
        product_columns = [product.mapped_tracking_no, product.order.order_no, product.name,
                           product.order.business.business_name, product.order.name, product.order.address1,
                           product.order.address2, " ", product.order.city, product.order.pincode,
                           product.order.state, product.order.phone, product.order.phone, product.name,
                           product.quantity, product.price if product.order.payment_method == 'C' else " ",
                           product.price, product.applied_weight, 0, 0, 0, 0, "77492",
                           product.order.business.business_name + " C/O: Sendd",
                           product.order.business.warehouse.address_line_1 +
                           product.order.business.warehouse.address_line_2, "8080028081",
                           product.order.business.warehouse.pincode,
                           product.order.business.business_name + " C/O: Sendd",
                           product.order.business.warehouse.address_line_1 +
                           product.order.business.warehouse.address_line_2, "8080028081",
                           product.order.business.warehouse.pincode]
        for j, product_column in enumerate(product_columns, 1):
            worksheet.write(excel_style(i, j), product_column)

    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=ecom" + date + ".xlsx"

    return response
