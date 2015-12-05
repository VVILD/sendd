import base64
import textwrap
from urllib import urlencode
from urllib2 import urlopen
import cStringIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from datetime import datetime
from django_project.celery import app
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage


@app.task
def send_business_labels(db_objs, business_obj):
    output = PdfFileWriter()
    name = business_obj.business_name
    phone = business_obj.contact_mob
    address = business_obj.get_full_address()
    for db_obj in db_objs:
        name2 = db_obj.name
        address2 = db_obj.get_full_address()
        phone2 = db_obj.phone
        s_method = db_obj.method
        p_method = db_obj.get_payment_method_display()
        date = str(db_obj.book_time.date())
        order_no = db_obj.order_no

        for product in db_obj.product_set.all():
            description = product.name
            weight = product.weight
            price = product.price
            sku = db_obj.reference_id
            trackingid = product.real_tracking_no
            params = urlencode({
                "name": name,
                "name2": name2,
                "phone": phone,
                "phone2": phone2,
                "address": address,
                "address2": address2,
                "s_method": s_method,
                "p_method": p_method,
                "date": date,
                "order_no": order_no,
                "description": description,
                "weight": weight,
                "price": price,
                "reference_id": sku,
                "trackingid": trackingid
            })

            response = urlopen("http://128.199.210.166/email_businesslabel.php?%s" % params).read()
            f1 = ContentFile(base64.b64decode(response))
            input1 = PdfFileReader(f1, strict=False)
            output.addPage(input1.getPage(0))

    outputStream = cStringIO.StringIO()
    output.write(outputStream)

    message = EmailMessage('Your shipping labels have arrived - Sendd',
                           'Hi {}, \n\n We have attached the shipping labels for the selected order/orders. \n\n '.format(
                               business_obj.business_name) +
                           'Thanks for choosing Sendd,\n Team Sendd',
                           'order@sendd.co',
                           [business_obj.email],
                           headers={'Reply-To': 'no-reply@sendd.co'})
    message.attach(str(business_obj.username) + "_" + str(datetime.now()) + '.pdf', outputStream.getvalue(),
                   'application/pdf')
    message.send(fail_silently=True)


@app.task
def business_sheet_uploader(reader, pickup_address, mem_file):
    from businessapp.models import Order, Product
    from core.models import Pincode
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
        except Exception as e:
            for o in orders_created:
                o.delete()
            for p in products_created:
                p.delete()
            message = EmailMessage(
                'There was an error processing the sheet for business {}. Error: {}'.format(pickup_address.company_name,
                                                                                            str(e)),
                'django-app@sendd.co', ['tech-support@sendd.co'], headers={'Reply-To': 'no-reply@sendd.co'})
            message.attach(str(pickup_address.company_name) + "_" + str(datetime.now()) + '.pdf', mem_file, 'text/csv')
            message.send()
            print("Email sent with the error message to tech-support")
        orders_created.append(order)
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
        except Exception as e:
            for o in orders_created:
                o.delete()
            for p in products_created:
                p.delete()
            message = EmailMessage(
                'There was an error processing the sheet for business {}. Error: {}'.format(pickup_address.company_name,
                                                                                            str(e)),
                'django-app@sendd.co', ['tech-support@sendd.co'], headers={'Reply-To': 'no-reply@sendd.co'})
            message.attach(str(pickup_address.company_name) + "_" + str(datetime.now()) + '.pdf', mem_file, 'text/csv')
            message.send()
            print("Email sent with the error message to tech-support")
        products_created.append(product)
    print("Sheet for {} uploaded successfully!".format(pickup_address.company_name))
