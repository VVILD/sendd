from django.db.models.signals import post_save
from myapp.models import Shipment

def send_update(sender, instance, created, **kwargs):
    if instance.real_tracking_no:
    	print "alu lelo"

post_save.connect(send_update, sender=Shipment)