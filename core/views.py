from django.core.files.base import ContentFile
from django.http import HttpResponseBadRequest
from django.shortcuts import render
import base64
from businessapp.models import Product
from core.utils.fedex_api_helper import Fedex
from myapp.models import Shipment

__author__ = 'vatsalshah'


def create_fedex_shipment(request):
    shipment_pk = request.GET.get('shipment_pk', None)
    client_type = request.GET.get('client_type', None)
    sender_name = None
    sender_phone = None
    sender_company = None
    sender_address1, sender_address2 = None, None
    sender_city = None
    sender_state = None
    sender_pincode = None
    sender_country_code = None
    is_business_sender = None
    receiver_name = None
    receiver_phone = None
    receiver_company = None
    receiver_address1, receiver_address2 = None, None
    receiver_city = None
    receiver_state = None
    receiver_pincode = None
    receiver_country_code = None
    is_business_receiver = None
    item_name = None
    item_weight = None
    service_type = None
    item_price = None
    fedex = Fedex()
    if client_type == 'business':
        product = Product.objects.get(pk=shipment_pk)
        if product.mapped_tracking_no:
            return HttpResponseBadRequest("Order already created")
        item_name = product.name
        item_weight = product.applied_weight
        sender_name = product.order.business.name
        sender_company = product.order.business.business_name
        sender_phone = product.order.business.contact_mob
        sender_address = product.order.business.address
        sender_address1, sender_address2 = sender_address[:len(sender_address) / 2], sender_address[
                                                                                     len(sender_address) / 2:]
        sender_city = product.order.business.city
        sender_state = product.order.business.state
        sender_pincode = product.order.business.pincode
        sender_country_code = 'IN'
        is_business_sender = True
        receiver_name = product.order.name
        receiver_company = None
        receiver_phone = product.order.phone
        receiver_address1 = product.order.address1
        receiver_address2 = product.order.address2
        receiver_city = product.order.city
        receiver_state = product.order.state
        receiver_pincode = product.order.pincode
        receiver_country_code = 'IN'
        is_business_receiver = False
        product_type = product.order.payment_method
        is_cod = False
        if product_type == 'C':
            is_cod = True
        service_type=fedex.get_service_type(product.order.method, product.price, is_cod)
        item_price = product.price
    elif client_type == 'customer':
        shipment = Shipment.objects.get(pk=shipment_pk)
        if shipment.mapped_tracking_no:
            return HttpResponseBadRequest
        item_name = shipment.item_name
        item_weight = shipment.weight
        sender_name = shipment.order.namemail.name
        sender_phone = shipment.order.user.phone
        sender_address = shipment.order.flat_no + shipment.order.address
        sender_address1, sender_address2 = sender_address[:len(sender_address) / 2], sender_address[
                                                                                     len(sender_address) / 2:]
        sender_city = "Mumbai"
        sender_state = "Maharashtra"
        sender_pincode = shipment.order.pincode
        sender_country_code = 'IN'
        is_business_sender = False
        receiver_name = shipment.drop_name
        receiver_company = None
        receiver_phone = shipment.drop_phone
        receiver_address = shipment.drop_address.flat_no + shipment.drop_address.locality
        receiver_address1, receiver_address2 = receiver_address[:len(receiver_address) / 2], receiver_address[
                                                                                             len(receiver_address) / 2:]
        receiver_city = shipment.drop_address.city
        receiver_state = shipment.drop_address.state
        receiver_pincode = shipment.drop_address.pincode
        receiver_country_code = 'IN'
        is_business_receiver = False
        service_type = fedex.get_service_type(shipment.category, shipment.price)
        item_price = shipment.price

    sender = {
        "name": sender_name,
        "company": sender_company,
        "phone": sender_phone,
        "address1": sender_address1,
        "address2": sender_address2,
        "city": sender_city,
        "state": sender_state,
        "pincode": sender_pincode,
        "is_business": is_business_sender,
        "country_code": sender_country_code
    }
    receiver = {
        "name": receiver_name,
        "company": receiver_company,
        "phone": receiver_phone,
        "address1": receiver_address1,
        "address2": receiver_address2,
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
    dropoff_type = 'REGULAR_PICKUP'
    result = fedex.create_shipment(sender, receiver, item, dropoff_type, service_type)
    label_url = None
    if result['status'] != 'ERROR':
        if client_type == 'business':
            product.mapped_tracking_no = result['tracking_number']
            # product.actual_cost = result['shipping_cost']
            product.fedex_label.save(result['tracking_number']+'.pdf', ContentFile(base64.b64decode(result['label'])))
            label_url = product.fedex_label.name
        elif client_type == 'customer':
            shipment.mapped_tracking_no = result['tracking_number']
            # shipment.actual_cost = result['shipping_cost']
            shipment.fedex_label = ContentFile(result['label'])
            shipment.save()
            label_url = shipment.fedex_label.name
    context = {
        "status": result['status'],
        "tracking_number": result["tracking_number"],
        "label_url": label_url
    }
    return render(request, 'fedex_new_shipment.html', {"result": context})