from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import cStringIO
from django.core.files.base import ContentFile
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
import base64
from businessapp.models import Product
from businessapp.models import Order as BusinessOrder
from myapp.models import Order as CustomerOrder
import core.utils.fedex_api_helper as fedex
from myapp.models import Shipment
from django.core.exceptions import ObjectDoesNotExist

__author__ = 'vatsalshah'


def create_fedex_shipment(request):
    order_pk = request.GET.get('order_pk', None)
    client_type = request.GET.get('client_type', None)
    data = []
    master_tracking_no = None
    shipping_cost = None
    fedex_ship_docs_url = None
    output = PdfFileWriter()
    if client_type == 'business':
        products = Product.objects.filter(order__pk=order_pk)
        package_count = products.count()
        for idx, product in enumerate(products, start=1):
            sender_details = None
            warehouse = None
            item_name = product.name
            item_weight = product.applied_weight
            item_qty = product.quantity
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
            service_type, config = fedex.get_service_type(str(product.order.method), float(product.price),
                                                          float(item_weight), receiver_city, is_cod)
            item_price = product.price
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
                "price": item_price,
                "quantity": item_qty
            }
            result = fedex.create_shipment(sender, receiver, item, config, service_type, idx, package_count, master_tracking_no)
            if result['status'] != 'ERROR':
                if product.mapped_tracking_no:
                    product.tracking_history= str(product.tracking_history) + ',' + str(product.mapped_tracking_no)
                product.mapped_tracking_no = result['tracking_number']
                if idx == 1:
                    master_tracking_no = result['tracking_number']


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

                if result['COMMERCIAL_INVOICE'] is not None:
                    f3 = ContentFile(base64.b64decode(result['COMMERCIAL_INVOICE']))
                    input3 = PdfFileReader(f3, strict=False)
                    output.addPage(input3.getPage(0))

                if result["shipping_cost"]:
                    shipping_cost = float(result["shipping_cost"])
                product.status = 'DI'
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
        shipments = Shipment.objects.filter(order__pk=order_pk)
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
                                                          float(item_weight), receiver_city)
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
            item = {
                "name": item_name,
                "weight": item_weight,
                "price": item_price
            }

            result = fedex.create_shipment(sender, receiver, item, config, service_type, idx, package_count, master_tracking_no)
            if result['status'] != 'ERROR':

                if shipment.mapped_tracking_no:
                    shipment.tracking_history=str(shipment.tracking_history) + ',' + str(shipment.mapped_tracking_no)
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
    context = {
        "data": data,
        "shipping_cost": shipping_cost,
        "fedex_ship_docs_url": fedex_ship_docs_url
    }
    return render(request, 'fedex_new_shipment.html', context)


def barcode_fedex_redirector(request, barcode):
    print(barcode)
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