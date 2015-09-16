from django.core.exceptions import ValidationError
from django.shortcuts import render
from businessapp.models import Order


def print_address_view(request):
    order_no = request.GET.get("order_no", None)
    if order_no is None:
        raise ValidationError("Please provide an order_no")
    order = Order.objects.get(pk=order_no)
    return render(request, 'PrintAddress.html', {"order": order})