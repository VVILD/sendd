data={"SE78969751":"M233273400","SE78969720":"M233273401","SE78969724":"M233273402","SE78969621":"M233273403","SE78969604":"M233273404","SE78969656":"M233273405","SE78969627":"M233273406","SE78969594":"M233273407","SE78969711":"M233273408","SE78969663":"M23327350","SE78969634":"M23327351","SE78969599":"M23327353","SE78969698":"M23327354","SE78968923":"M23327355","SE78969740":"M23327356","SE78967523":"M23327357","SE78969626":"M23327358","SE78967803":"M23327359","se78969748":"M23327360","SE78967681":"M23327361","SE78967705":"M23327363","SE78969721":"M23327364","SE78969710":"M23327365","SE78969571":"M23327366","SE78969565":"M23327367","SE78969567":"M23327368","SE78969613":"M23327369","SE78969749":"M23327362","SE78969569":"M23327370","SE78967901":"M23327371","SE78968885":"M23327372","SE78969520":"M23327373","SE78969742":"M23327374","SE78969582":"M23327375","SE78969485":"M23327376","SE78969488":"M23327377","SE78968884":"M23327378","SE78969726":"M23327379","SE78969665":"M23327380","SE78969727":"M23327381","SE78969603":"M23327382","SE78969725":"M23327383","SE78969723":"M23327384","SE78967568":"M23327385","SE78968886":"M23327386","se78969498":"M23327387","SE78969737":"M23327388","SE78969743":"M23327389","SE78968919":"M23327390","SE78967785":"M23327392","SE78969652":"M23327393","SE78968887":"M23327394","SE78969728":"M23327395","SE78967936":"M23327396","SE78969484":"M23327397","SE78969575":"M23327398","SE78969502":"M23327399"}

#data={"SE78969751":"M233273400","SE78969720":"M233273401"}


from django.core.management.base import BaseCommand
from businessapp.models import Product
from myapp.models import Shipment
import easypost
import aftership
api = aftership.APIv4('c46ba2ea-5a3e-43c9-bda6-793365ec1ebb')
import json
import time
import dateutil.parser
import datetime
import urllib
import re
import datetime	



easypost.api_key = 'UX9cFcEOVCEvw32QgFjXBg'


format='%Y-%m-%d %H:%M:%S'


def remove_non_ascii_1(text):
	return ''.join(i for i in text if ord(i)<128)


class Command(BaseCommand):
  args = 'Arguments is not needed'
  help = 'Django admin custom command poc.'
 
  def handle(self, *args, **options):

  	for barcode in data:
  		product=Product.objects.get(barcode=barcode)
  		product.mapped_tracking_no=data[barcode]
  		product.company='DT'
  		product.save()


