import base64
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
                           'Hi {}, \n\n We have attached the shipping labels for the selected order/orders. \n\n '.format(business_obj.business_name) +
                           'Thanks for choosing Sendd,\n Team Sendd',
                           'order@sendd.co',
                           [business_obj.email],
                           headers={'Reply-To': 'no-reply@sendd.co'})
    message.attach(str(business_obj.username)+"_"+str(datetime.now())+'.pdf', outputStream.getvalue(), 'application/pdf')
    message.send(fail_silently=True)