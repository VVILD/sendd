from django.core.management.base import BaseCommand
from businessapp.models import Product, Order
from myapp.models import Shipment
import easypost
import aftership
api = aftership.APIv4('c46ba2ea-5a3e-43c9-bda6-793365ec1ebb')
import json
import time
import dateutil.parser
import datetime
import urllib
import requests
from datetime import date,timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags




class Command(BaseCommand):
  args = 'Arguments is not needed'
  help = 'Django admin custom command poc.'

  def handle(self, *args, **options):

      y=Order.objects.filter(business__send_notification='Y',notification='N')



      for order in y:
          phone=urllib.quote_plus(str(order.phone))
          business_name=urllib.quote_plus(str(order.business.business_name))
          sent_date=urllib.quote_plus(str(date.today()))
          delivery_date=urllib.quote_plus(str(date.today()+timedelta(days=5)))
          tracking_id=urllib.quote_plus(str(order.master_tracking_number))
          name=urllib.quote_plus(str(order.name))
          msg0 = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
          msga = str(phone)
          msg1="&msg=Dear+"+name+"%0D%0ASeller+"+business_name+"+has+shipped+your+parcel+1+via+Sendd+on+"+sent_date+".+Your+product+is+estimated+to+be+delivered+by+"+delivery_date+".+You+can+track+your+order+at+http%3A%2F%2Fsendd.co%2Ftrack.html%3FtrackingID%3D"+tracking_id+"&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&format=text"
          query = ''.join([msg0, msga, msg1])
          print query
          req=requests.get(query)


          subject, from_email, to = 'Hi', 'vatsal@sendd.co', 'sargun@sendd.co'
          html_content = render_to_string('orderconfirmationmail.html', {'name':name,'business_name':business_name,'sent_date':sent_date,'delivery_date':delivery_date,'tracking_id':tracking_id})
          print html_content
          text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.
          msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
          msg.attach_alternative(html_content, "text/html")
          msg.send()
          print msg.send()

