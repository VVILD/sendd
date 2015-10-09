from django.core.exceptions import ValidationError
from django.shortcuts import render
from businessapp.models import Order
from PyPDF2 import PdfFileWriter, PdfFileReader
import cStringIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def print_address_view(request):
    order_no = request.GET.get("order_no", None)
    if order_no is None:
        raise ValidationError("Please provide an order_no")
    order = Order.objects.get(pk=order_no)
    return render(request, 'PrintAddress.html', {"order": order})

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