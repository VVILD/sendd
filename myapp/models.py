import random
import uuid
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models.signals import post_save
from django.db import models
from django.core.validators import RegexValidator
import hashlib
from datetime import datetime, timedelta
from pytz import timezone
from push_notifications.models import GCMDevice
from core.fedex.base_service import FedexError
from core.models import Warehouse, Pincode
from core.utils import state_matcher
from pickupboyapp.models import PBUser
import urllib2

import requests
import json
import urllib



class User(models.Model):
    phone_regex = RegexValidator(regex=r'^[0-9]*$',
                                 message="Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=12, primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=300, null=True, blank=True)
    email = models.EmailField(max_length=75, null=True, blank=True)
    otp = models.IntegerField(null=True, blank=True)
    apikey = models.CharField(max_length=100, null=True, blank=True)
    referral_code = models.CharField(max_length=50, null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    gcmid = models.TextField(null=True, blank=True)
    deviceid = models.CharField(max_length=25, null=True, blank=True)

    def save(self, *args, **kwargs):
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        self.time = ind_time
        super(User, self).save(*args, **kwargs)


    def __unicode__(self):
        return str(self.phone)


class Address(models.Model):
    flat_no = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=30, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)

    def __unicode__(self):
        return str(self.flat_no)+','+str(self.locality)+','+str(self.city)+','+str(self.state)+','+str(self.country)+'-'+str(self.pincode)

    def save(self, *args, **kwargs):
        if not state_matcher.is_state(self.state):
            closest_state = state_matcher.get_closest_state(self.state)
            if closest_state:
                self.state = closest_state[0]
        super(Address, self).save(*args, **kwargs)



class Namemail(models.Model):
    nm_no = models.AutoField(primary_key=True)
    name = models.CharField(max_length=160, null=True, blank=True)
    email = models.EmailField(max_length=75, null=True, blank=True)
    user = models.ForeignKey(User)


class Promocode(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    msg = models.CharField(max_length=150)
    only_for_first = models.CharField(max_length=1, choices=(('Y', 'yes'), ('N', 'no'),), )
    one_time = models.CharField(max_length=1, choices=(('Y', 'yes'), ('N', 'no'),), blank=True, null=True )
    promocode_type = models.CharField(max_length=1, choices=(('P', 'percentage'), ('S', 'sum'),), blank=True, null=True)
    promocode_amount = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=False)
    expiry = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return str(self.code)


class Order(models.Model):
    order_no = models.AutoField(primary_key=True)
    date = models.DateField(verbose_name='pickup date', null=True, blank=True)
    time = models.TimeField(verbose_name='pickup time', null=True, blank=True)
    user = models.ForeignKey(User)
    promocode = models.ForeignKey(Promocode, null=True, blank=True)

    namemail = models.ForeignKey(Namemail, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=75, null=True, blank=True)
    status = models.CharField(max_length=1,
                              choices=(('P', 'pending'), ('C', 'complete'), ('N', 'cancelled'), ('F', 'fake'),),
                              default='P')

    order_status = models.CharField(max_length=2,
                                    choices=(
                                        ('O', 'order_recieved'), ('AP', 'Approved'),('A', 'Alloted'), ('P', 'picked up'), ('Pa', 'packed'),
                                        ('C', 'completed'), ('D', 'delivered'), ('N', 'cancelled'), ('F', 'fake'),
                                        ('Q', 'query'), ('DI', 'dispatched'),), null=True, blank=True, default='O')

    comment = models.TextField(null=True, blank=True)
    cs_comment = models.TextField(null=True, blank=True)
    
    way = models.CharField(max_length=1,
                           choices=(('A', 'app'), ('W', 'web'), ('C', 'call'),),
                           default='A')
    pick_now = models.CharField(max_length=1,
                                choices=(('Y', 'yes'), ('N', 'no'),),
                                default='Y')
    pb = models.ForeignKey(PBUser, null=True, blank=True)
    latitude = models.DecimalField(max_digits=25, decimal_places=20, null=True, blank=True)
    longitude = models.DecimalField(max_digits=25, decimal_places=20, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    pincode = models.CharField(max_length=30, null=True, blank=True)
    flat_no = models.CharField(max_length=100, null=True, blank=True)
    book_time = models.DateTimeField(null=True, blank=True)
    warehouse = models.ForeignKey(Warehouse, null=True, blank=True, related_name="myapp_orders")
    master_tracking_number = models.CharField(max_length=10, blank=True, null=True)
    mapped_master_tracking_number = models.CharField(max_length=50, blank=True, null=True)
    fedex_ship_docs = models.FileField(upload_to='shipment/', blank=True, null=True)

    def __unicode__(self):
        return str(self.order_no)

    def save(self, *args, **kwargs):
        if self.pb and self.order_status=='AP':

            self.order_status='A'
            address= str(self.flat_no) + str(self.address) +str(self.pincode)  
            
            phone=urllib.quote_plus(str(self.pb.phone))
            user_phone=urllib.quote_plus(str(self.user.phone))
            order_no=urllib.quote_plus(str(self.pk))
            name=urllib.quote_plus(str(self.namemail.name))
            msg0 = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
            msga = str(phone)
            msg1 = "&msg=Pickup+details+for+order+no%3A"+str(order_no)+".%0D%0AName%3A"+str(name)+"%2C+Address%3A"+str(address)+"%2C+Mobile+No%3A"+str(user_phone)+"&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&format=text"
            query = ''.join([msg0, msga, msg1])
            req = requests.get(query)

        ''' On save, update timestamps '''
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        if not self.pk:
            self.book_time = ind_time
            super(Order, self).save(*args, **kwargs)
            order_no = self.pk + 1000
            if str(order_no) > 4:
                order_no = str(order_no)[:4]
            self.master_tracking_number = 'M' + order_no + str(uuid.uuid4().get_hex().upper()[:5])
        if not self.warehouse:
            pincode = Pincode.objects.filter(pincode=self.pincode).exclude(latitude__isnull=True)
            try:
                self.warehouse = pincode[0].warehouse
            except:
                self.warehouse=Warehouse.objects.get(pk=1)
        super(Order, self).save(*args, **kwargs)


class ReceivedOrder(Order):
    class Meta:
        proxy = True


class AllotedOrder(Order):
    class Meta:
        proxy = True


class PickedupOrder(Order):
    class Meta:
        proxy = True

class DispatchedOrder(Order):
    class Meta:
        proxy = True

class ApprovedOrder(Order):
    class Meta:
        proxy = True

class CancelledOrder(Order):
    class Meta:
        proxy = True

class ApprovedOrderCs(Order):
    class Meta:
        proxy = True


class CompletedOrder(Order):
    class Meta:
        proxy = True


class FakeOrder(Order):
    class Meta:
        proxy = True


class QueryOrder(Order):
    class Meta:
        proxy = True


class Shipment(models.Model):
    weight = models.CharField(verbose_name='item weight', max_length=10, null=True, blank=True)
    price = models.CharField(max_length=10, null=True, blank=True)

    name = models.CharField(verbose_name='item name', max_length=50, null=True, blank=True)

    tracking_no = models.AutoField(primary_key=True)
    real_tracking_no = models.CharField(max_length=10, blank=True, null=True)
    mapped_tracking_no = models.CharField(max_length=50, null=True, blank=True)
    tracking_data = models.CharField(max_length=8000, null=True, blank=True)
    img = models.ImageField(upload_to='shipment/', null=True, blank=True)
    category = models.CharField(max_length=1,
                                choices=(('P', 'premium'), ('S', 'standard'), ('E', 'economy'),),
                                default='P', blank=True, null=True)
    drop_name = models.CharField(max_length=100, null=True, blank=True)

    phone_regex2 = RegexValidator(regex=r'^[0-9]{10,11}$',
                                  message="Phone number must be entered in the format: '999999999'. And be of 10 digits.")

    drop_phone = models.CharField(validators=[phone_regex2], max_length=16, null=True, blank=True)
    drop_address = models.ForeignKey(Address, null=True, blank=True)
    order = models.ForeignKey(Order, null=True, blank=True)

    status = models.CharField(max_length=2,
                              choices=(('P', 'pending'), ('C', 'complete'), ('PU', 'pickedup'), ('CA', 'cancelled'), ('DI', 'dispatched')),
                              default='P', null=True, blank=True)

    paid = models.CharField(max_length=10,
                            choices=(('Paid', 'Paid'), ('Not Paid', 'Not Paid'),),
                            blank=True, null=True, default='Not Paid')

    company = models.CharField(max_length=2,
                               choices=[('F', 'FedEx'), ('D', 'Delhivery'), ('P', 'Professional'), ('G', 'Gati'),
                                        ('A', 'Aramex'), ('E', 'Ecomexpress'), ('DT', 'dtdc'), ('FF', 'First Flight'),
                                        ('M', 'Maruti courier'), ('I', 'India Post'), ('S', 'Sendd'), ('B', 'Bluedart'), ('T', 'trinity'), ('V', 'vichare'), ('DH', 'dhl'), ('S', 'skycom')],
                               blank=True, null=True)

    cost_of_courier = models.CharField(verbose_name='item cost', max_length=100, null=True, blank=True)
    item_name = models.CharField(max_length=100, null=True, blank=True)
    kartrocket_order = models.CharField(max_length=100, null=True, blank=True)
    barcode = models.CharField(null=True, blank=True, default=None, max_length=12, unique=True)
    fedex_cod_return_label = models.FileField(upload_to='shipment/', blank=True, null=True)
    fedex_outbound_label = models.FileField(upload_to='shipment/', blank=True, null=True)
    fedex_ship_docs = models.FileField(upload_to='shipment/', blank=True, null=True)
    actual_shipping_cost = models.FloatField(default=0.0)
    fedex_check = models.CharField(max_length=1,
                                   choices=(('I', 'Integrity Check'), ('O', 'ODA'), ('R', 'Restricted States'), ('P', 'Pass'), ('S', 'State Integrity Check'), ('A', 'Address Integrity Check'), ('N', 'Not Servicable'), ('Z', 'Invalid Pincode')),
                                   default='I')
    is_document = models.BooleanField(default=False)
    is_fragile = models.BooleanField(default=False)
    __original_tracking_data = None
    update_time=models.DateTimeField(null=True, blank=True)
    dispatch_time=models.DateTimeField(null=True, blank=True)
    
    qc_comment=models.TextField(null=True, blank=True)
    tracking_history = models.TextField(null=True, blank=True)
    warning = models.BooleanField(default=False)
    last_tracking_status=models.CharField(max_length=300, null=True, blank=True)
    actual_delivery_timestamp = models.DateTimeField(blank=True, null=True)
    estimated_delivery_timestamp = models.DateTimeField(blank=True, null=True)


    
    def __init__(self, *args, **kwargs):
        super(Shipment, self).__init__(*args, **kwargs)
        self.__original_tracking_data = self.tracking_data

    def save(self, *args, **kwargs):

        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now()
        time = ind_time
        if self.mapped_tracking_no and (self.status=='PU' or self.status=='DI' or self.status=='P'):
            self.status='DI'
            self.update_time=time
            self.dispatch_time=time
            self.last_tracking_status=json.loads(self.tracking_data)[-1]['status']
            #Warnings rule definations
            if ('exception' in self.last_tracking_status):
                self.warning=True


        if self.tracking_data != self.__original_tracking_data:
            self.update_time=time


        if not self.pk:
            print self.pk
            z = timezone('Asia/Kolkata')
            fmt = '%Y-%m-%d %H:%M:%S'
            ind_time = datetime.now(z)
            time = ind_time
            self.update_time = ind_time
            time = str(time.replace(second=0, microsecond=0,tzinfo=None))
            self.tracking_data = "[{\"status\": \"Booking Received\", \"date\"	: \"" + time + " \", \"location\": \"Mumbai (Maharashtra)\"}]"
            print self.tracking_data
            print self.status
            super(Shipment, self).save(*args, **kwargs)
            print self.pk
            alphabet = random.choice('BDQP')
            no1 = random.choice('1234567890')
            no2 = random.choice('1234567890')
            no = int(self.pk) + 134528
            trackingno = 'S' + str(no) + str(alphabet) + str(no1) + str(no2)
            print trackingno
            self.real_tracking_no = trackingno

            kwargs['force_update'] = True
            kwargs['force_insert'] = False
            super(Shipment, self).save(*args, **kwargs)

        if (self.barcode is not None) and (len(self.barcode) > 12 or len(self.barcode) < 10):
            raise ValidationError("Barcode length should be 10")

        super(Shipment, self).save(*args, **kwargs)



class QcShipment(Shipment):
    class Meta:
        proxy = True

class Forgotpass(models.Model):
    user = models.ForeignKey(User)
    auth = models.CharField(max_length=100)
    time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        self.time = ind_time
        super(Forgotpass, self).save(*args, **kwargs)


class X(models.Model):
    Name = models.CharField(max_length=100)
    C = models.ImageField(upload_to='shipment/')
    order = models.ForeignKey(Order, null=True)


class LoginSession(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    success = models.CharField(max_length=100,
                               choices=(('notregistered', 'notregistered'), ('wrongpassword', 'wrongpassword'),
                                        ('success', 'success'),),
                               default='wrongpassword')

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        if not self.pk:
            self.time = ind_time
        super(LoginSession, self).save(*args, **kwargs)


class Weborder(models.Model):
    item_details = models.CharField(max_length=100)
    pickup_location = models.CharField(max_length=4000)
    pincode = models.CharField(max_length=56)
    number = models.CharField(max_length=51)
    time = models.DateTimeField(null=True, blank=True)


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        self.time = ind_time
        super(Weborder, self).save(*args, **kwargs)


class Priceapp(models.Model):
    weight = models.CharField(max_length=10)
    pincode = models.CharField(max_length=60)
    l = models.CharField(max_length=10)
    b = models.CharField(max_length=10)
    h = models.CharField(max_length=10)


class Dateapp(models.Model):
    pincode = models.CharField(max_length=60)


class Gcmmessage(models.Model):
    title = models.CharField(max_length=60)
    message = models.TextField()

    def __unicode__(self):
        return str(self.message)


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        try:
            devices = GCMDevice.objects.all()
            devices.send_message(self.message, extra={"title": self.title})
        # device = GCMDevice.objects.get(registration_id='APA91bEjN-CdfjLJd4PGJRu4z3k0pbY8wndZddW2tIc5mcsU_b6UhjgbOLDniWYYd_9GZ4MPPAwh0Wva-_dPsl-fabuteKKV262VljMCt3msxhmoCBcGrq675OLw8zIQYzxopHqfeGgQ')
        #device.send_message("harsh bahut bada chakka hai.harsh", extra={"tracking_no": "S134807P31","url":"http://128.199.159.90/static/IMG_20150508_144433.jpeg"})
        except:
            pass
        super(Gcmmessage, self).save(*args, **kwargs)


class Promocheck(models.Model):
    code = models.CharField(max_length=20)
    user = models.ForeignKey(User, null=True, blank=True)
    valid = models.CharField(max_length=1, choices=(('Y', 'yes'), ('N', 'no'),), )


class Pincodecheck(models.Model):
    pincode = models.CharField(max_length=6)

    def __unicode__(self):
        return str(self.pincode)


def send_update(sender, instance, created, **kwargs):
# product can be pending complete returned picked up
# choices=(('P', 'pending'), ('C', 'complete'), ('PU', 'pickedup'), ('CA', 'cancelled'), ('R', 'return')),
# ('P', 'pending'), ('C', 'complete'), ('N', 'cancelled'), ('D', 'in transit'), ('PU', 'pickedup')), default='P')
# order will be pending intransit complete cancelled picked up
    products_in_order = Shipment.objects.filter(order=instance.order)
        
    count=0
    if ((instance.status == 'PU') or (instance.status == 'CA')) and (instance.order.order_status=='A'):
        pickedup = True
        print "count of shipments"
        print products_in_order.count()
        for product in products_in_order:
            if (product.status!='PU') & (product.status!='CA'):
                pickedup=False
        if (pickedup):
# signals.post_save.disconnect(send_update_order, sender=Order)
            instance.order.order_status = 'P'

            instance.order.save()
            print "i was here"
            print count
            rturn=send_invoice_custom(instance.order)
            print rturn

    if (instance.status == 'DI') or (instance.status == 'CA'):
        Dispatched = True
        for product in products_in_order:
            if (product.status!='DI') & (product.status!='CA'):
                Dispatched=False
        if (Dispatched):
# signals.post_save.disconnect(send_update_order, sender=Order)
            instance.order.order_status = 'DI'
            instance.order.save()


    if (instance.status=='CA'):
        Cancelled=True
        for product in products_in_order:
            if (product.status!='CA'):
                Cancelled=False
        if (Cancelled):
# signals.post_save.disconnect(send_update_order, sender=Order)
            instance.order.order_status = 'N'
            instance.order.save()
        

# signals.post_save.connect(send_update_order, sender=Order)
post_save.connect(send_update, sender=Shipment)

class Zipcode(models.Model):
    pincode = models.CharField(max_length=6, primary_key=True)
    zone = models.CharField(max_length=1)
    city = models.CharField(max_length=56)
    state = models.CharField(max_length=56)
    cod = models.BooleanField(default=False)
    fedex = models.BooleanField(default=False)
    aramex = models.BooleanField(default=False)
    delhivery = models.BooleanField(default=False)
    ecom = models.BooleanField(default=False)
    firstflight = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.pincode)


class Invoicesent(models.Model):
    order = models.ForeignKey(Order)





def send_invoice_custom(obj):
    valid = 1
    e_string = ''
    invoice_dict = {}
    total = 0
    order_no = obj.order_no
    invoice_dict['orderno'] = order_no

    try:
        times = Invoicesent.objects.filter(order=obj.order_no)
        times_count = str(times.count()) + ' invoices sent'
    except:
        times_count = "0 invoices sent"

    try:
        name = obj.namemail.name
        invoice_dict['name'] = name
    except:
        e_string = e_string + 'name not set <br>'
        valid = 0

    try:
        address = obj.address
        invoice_dict['address'] = address
    except:
        e_string = e_string + 'address not set <br>'
        valid = 0

    try:
        email = obj.namemail.email
        invoice_dict['mailto'] = email
    except:
        e_string = e_string + 'email not set <br>'

    try:
        book_time = obj.book_time
        invoice_dict['date'] = str(book_time)[0:10]
    except:
        e_string = e_string + 'time not set <br>'

    try:
        shipments = Shipment.objects.filter(order=obj.order_no)
        number = shipments.count()
        invoice_dict['numberofshipment'] = number
        count = 0
        total = 0
        for s in shipments:
            try:

                print s.real_tracking_no
                print s.drop_address.pincode
                print s.weight
                print 'check'

                if s.weight is None or s.weight.strip() == '':
                    e_string = e_string + str(s.real_tracking_no) + ' weight not set <br>'
                    valid = 0
                if s.drop_address.pincode is None:
                    e_string = e_string + str(s.real_tracking_no) + ' drop_address pincode not set <br>'
                    valid = 0
                if s.price is None or s.price.strip() == '':
                    e_string = e_string + str(s.real_tracking_no) + ' price not set <br>'
                    valid = 0

                try:
                    invoice_dict['des' + str(count)] = str(s.weight) + ' kg to ' + str(s.drop_address.pincode)
                    invoice_dict['tracking' + str(count)] = str(s.real_tracking_no)
                    invoice_dict['price' + str(count)] = str(s.price)
                    invoice_dict['total' + str(count)] = str(s.price)
                    invoice_dict['quantity' + str(count)] = '1'
                    total = total + int(s.price)
                except Exception, e:
                    print str(e)

                count = count + 1
            except Exception, e:
                print str(e)
                e_string = e_string + 'error in fetching shipments <br>'
                valid = 0

            invoice_dict['overalltotal'] = total


    except:
        e_string = e_string + 'number of xx shipments not set <br>'
        valid = 0




    #           address=obj.address
    #           shipments = Shipment.objects.filter(order=obj.order_no)
    #           mail_subject="a"
    #           mail_content="ggh"
    if (valid):

        query='http://128.199.210.166/payment_invoice.php?'+urllib.urlencode(invoice_dict)
        print query
        return requests.get(query)

        # return '%s <br> <a target="_blank" href="http://128.199.210.166/payment_invoice.php?%s">generate  and send invoice to %s</a>' % (
        #     times_count, urllib.urlencode(invoice_dict), invoice_dict['mailto'])
    else:
        return e_string
