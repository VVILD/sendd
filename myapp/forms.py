from django.forms import ModelForm, Textarea
from myapp.models import Shipment

class ShipmentForm(ModelForm):
    class Meta:
        model = Shipment
        widgets = {
            'tracking_data': Textarea(attrs={'cols': 80, 'rows': 20}),
        }