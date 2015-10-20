import uuid
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
# from django.contrib.auth.models import User
from datetime import datetime
from geopy.distance import vincenty
from geopy.geocoders import googlev3
from pytz import timezone
from django.db.models.signals import post_save
import hashlib
import random
# Create your models here.
import math
from django.contrib.auth.models import User

from django.db.models import signals
from core.fedex.base_service import FedexError
from core.models import Warehouse, Pincode
from core.utils import state_matcher
from django.core.exceptions import ObjectDoesNotExist
import json
import urllib
import requests


class Profile(models.Model):
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=100)
    usertype = models.CharField(max_length=1, choices=(
    ('O', 'ops'), ('B', 'bd'), ('A', 'admin'), ('Q', 'qc'), ('C', 'customer support'),),
                                null=True, blank=True)

    def __unicode__(self):
        return str(self.user.username)


# class BusinessManager(models.Model):
# """User with app settings."""
# phone = models.CharField(max_length=50)
# user = models.OneToOneField(User)
# # Use UserManager to get the create_user method, etc.




# class BusinessManager(User):
# """User with app settings."""
#     phone = models.CharField(max_length=50)
from pickupboyapp.models import PBUser

# class CustomBusinessManager(models.Manager):
#     def get_query_set(self):
#         return super(CustomerManager, self).get_query_set().annotate(models.Count('order'))

from random import randint


class Weight(models.Model):
    weight = models.FloatField()

    def __unicode__(self):
        return str(self.weight)


class Zone(models.Model):
    zone = models.CharField(max_length=2)

    def __unicode__(self):
        return str(self.zone)


class Business(models.Model):
    # phone_regex = RegexValidator(regex=r'^[0-9]*$', message="Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")
    username = models.CharField(max_length=20, primary_key=True)
    apikey = models.CharField(max_length=100, null=True, blank=True)
    business_name = models.CharField(max_length=100)
    password = models.CharField(max_length=300)
    email = models.EmailField(max_length=75)
    name = models.CharField(max_length=100)
    tin = models.CharField(max_length=100, null=True, blank=True)
    contact_mob = models.CharField(max_length=15)
    contact_office = models.CharField(max_length=15, null=True, blank=True)
    pickup_time = models.CharField(max_length=1, choices=(('M', 'morning'), ('N', 'noon'), ('E', 'evening'),),
                                   null=True, blank=True)
    address = models.CharField(max_length=315, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    # key=models.CharField(max_length = 100,null=True,blank =True)
    businessmanager = models.ForeignKey(Profile, null=True, blank=True)
    show_tracking_company = models.CharField(max_length=1, choices=(('Y', 'yes'), ('N', 'no'),), null=True, blank=True,
                                             default='N')
    send_notification = models.CharField(max_length=1, choices=(('Y', 'yes'), ('N', 'no'),), null=True, blank=True,
                                         default='N')
    pb = models.ForeignKey(PBUser, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    assigned_pickup_time = models.TimeField(null=True, blank=True)
    #     # Use UserManager to get the create_user method, etc.
    #     objects = UserManager()

    cs_comment = models.TextField(null=True, blank=True)
    ff_comment = models.TextField(null=True, blank=True)

    daily = models.BooleanField(default=False)
    status = models.CharField(max_length=1,
                              choices=(('Y', 'approved'), ('N', 'not approved'), ('C', 'cancelled'), ('A', 'alloted'),),
                              null=True, blank=True,
                              default='N')
    warehouse = models.ForeignKey(Warehouse, null=True, blank=True)
    cod_sum=models.FloatField(default=40.0)
    cod_percentage=models.FloatField(default=1.5)
    discount_percentage=models.FloatField(default=0.0)

    class Meta:
        ordering = ['business_name', ]

    def get_full_address(self):
        return str(self.address + " " + self.city + " " + self.state + " - " + self.pincode)

    def save(self, *args, **kwargs):


        if self.pb and self.status == 'Y':
            self.status = 'A'
            address = urllib.quote_plus(str(self.address))
            phone = urllib.quote_plus(str(self.pb.phone))
            user_phone = urllib.quote_plus(str(self.contact_office) + str(self.contact_mob))
            order_no = urllib.quote_plus(str(self.pk))
            name = urllib.quote_plus(str(self.name))
            msg0 = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to="
            msga = str(phone)
            msg1 = "&msg=Pickup+details+for+order+no%3A" + str(order_no) + ".%0D%0AName%3A" + str(
                name) + "%2C+Address%3A" + str(address) + "%2C+Mobile+No%3A" + str(
                user_phone) + "&msg_type=TEXT&userid=2000142364&auth_scheme=plain&password=h0s6jgB4N&format=text"
            query = ''.join([msg0, msga, msg1])
            print query
            req = requests.get(query)

        if not self.apikey:
            self.apikey = hashlib.sha1(str(random.getrandbits(256))).hexdigest()
        if self.pincode and not self.warehouse:
            pincode = Pincode.objects.filter(pincode=self.pincode).exclude(latitude__isnull=True)
            if len(pincode) > 0:
                self.warehouse = pincode[0].warehouse
        super(Business, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.business_name)


class NotApprovedBusiness(Business):
    class Meta:
        proxy = True


class BusinessPricing(Business):
    class Meta:
        proxy = True


class ApprovedBusiness(Business):
    class Meta:
        proxy = True


class ApprovedBusinessOP(Business):
    class Meta:
        proxy = True


class AllotedBusiness(Business):
    class Meta:
        proxy = True


class PickedupBusiness(Business):
    class Meta:
        proxy = True


class DailyBusiness(Business):
    class Meta:
        proxy = True

class Bdheadpanel(Business):
    class Meta:
        proxy = True
        verbose_name_plural = "bdheadpanel"

class CancelledBusiness(Business):
    class Meta:
        proxy = True

class CodBusinessPanel(Business):
    class Meta:
        proxy = True
        verbose_name_plural = "CodBusinessPanel"


class LoginSession(models.Model):
    Business = models.ForeignKey(Business, null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    msg = models.CharField(max_length=100,
                           choices=(('notregistered', 'notregistered'), ('wrongpassword', 'wrongpassword'),
                                    ('success', 'success'),),
                           default='wrongpassword')

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        if not self.pk:
            self.time = ind_time.strftime(fmt)
        super(LoginSession, self).save(*args, **kwargs)


class Order(models.Model):
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    third_party_id = models.CharField(max_length=100, null=True, blank=True)
    order_no = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=12)
    email = models.EmailField(max_length=75, null=True, blank=True)
    address1 = models.CharField(max_length=300, null=True, blank=True)
    address2 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=30, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    payment_method = models.CharField(max_length=1, choices=(('F', 'Free Shipping'), ('C', 'cod'),), )
    book_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=(
        ('P', 'pending'), ('C', 'complete'), ('N', 'cancelled'), ('D', 'in transit'), ('PU', 'pickedup'),
        ('RC', 'return/completed'), ('R', 'return'), ('DI', 'dispatched'),), default='P')
    confirmed = models.BooleanField(default=True)
    method = models.CharField(max_length=1,
                              choices=(('B', 'Bulk'), ('N', 'Normal'),),
                              blank=True, null=True)
    master_tracking_number = models.CharField(max_length=10, blank=True, null=True)
    mapped_master_tracking_number = models.CharField(max_length=50, blank=True, null=True)
    fedex_ship_docs = models.FileField(upload_to='shipment', blank=True, null=True)
    business = models.ForeignKey(Business)
    notification = models.CharField(max_length=1, choices=(('Y', 'yes'), ('N', 'no'),), null=True, blank=True,
                                         default='N')
    last_updated_status = models.DateTimeField(null=True, blank=True)
    __status = None
    ff_comment=models.TextField(null=True, blank=True)
    refund = models.FloatField(default=0.0)


    def __unicode__(self):
        return str(self.order_no)

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        if self.status:
            self.__status = self.status

    def get_full_address(self):
        return str(self.address1 + " " + self.address2 + " " + self.city + " " + self.state + " - " + self.pincode)

    def save(self, *args, **kwargs):
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

        if self.status != self.__status or not self.last_updated_status:
            self.last_updated_status = datetime.now()

        if self.state:
            if not state_matcher.is_state(self.state):
                closest_state = state_matcher.get_closest_state(self.state)
                if closest_state:
                    self.state = closest_state[0]
        super(Order, self).save(*args, **kwargs)



class Product(models.Model):
    name = models.TextField(null=True, blank=True)
    quantity = models.IntegerField(max_length=10, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(default=0.0)
    weight = models.FloatField(max_length=10, null=True, blank=True)
    applied_weight = models.FloatField(max_length=10, null=True, blank=True)
    order = models.ForeignKey(Order, null=True, blank=True)
    real_tracking_no = models.CharField(max_length=10, blank=True, null=True)
    mapped_tracking_no = models.CharField(max_length=50, null=True, blank=True)
    tracking_data = models.TextField(null=True, blank=True)
    kartrocket_order = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=2,
                               choices=[('F', 'FedEx'), ('D', 'Delhivery'), ('P', 'Professional'), ('G', 'Gati'),
                                        ('A', 'Aramex'), ('E', 'Ecomexpress'), ('DT', 'dtdc'), ('FF', 'First Flight'),
                                        ('M', 'Maruti courier'), ('I', 'India Post'), ('S', 'Sendd'), ('B', 'bluedart'),
                                        ('T', 'trinity'), ('V', 'vichare'), ('DH', 'dhl'), ('SK', 'skycom'), ('NA', 'nandan'),('FA','Fast train'),('TE','Tej')],
                               blank=True, null=True)
    shipping_cost = models.FloatField(default=0.0)
    cod_cost = models.FloatField(default=0.0)
    return_cost = models.FloatField(default=0.0)

    # tracking_no=models.AutoField(primary_key=True)
    barcode = models.CharField(null=True, blank=True, default=None, max_length=12, unique=True)
    status = models.CharField(max_length=2,
                              choices=(('P', 'pending'), ('C', 'complete'), ('PU', 'pickedup'), ('CA', 'cancelled'),
                                       ('R', 'return'), ('DI', 'dispatched')),
                              default='P')

    date = models.DateTimeField(null=True, blank=True)
    remittance = models.BooleanField(default=False)
    fedex_cod_return_label = models.FileField(upload_to='shipment/', blank=True, null=True)
    fedex_outbound_label = models.FileField(upload_to='shipment/', blank=True, null=True)
    fedex_ship_docs = models.FileField(upload_to='shipment/', blank=True, null=True)
    actual_shipping_cost = models.FloatField(default=0.0)
    is_document = models.BooleanField(default=False)
    is_fragile = models.BooleanField(default=False)

    __original_tracking_data = None
    update_time = models.DateTimeField(null=True, blank=True)
    dispatch_time = models.DateTimeField(null=True, blank=True)

    remittance_date = models.DateTimeField(null=True, blank=True)

    qc_comment = models.TextField(null=True, blank=True)
    tracking_history = models.TextField(null=True, blank=True)
    warning = models.BooleanField(default=False)

    warning_type = models.CharField(max_length=3,blank=True,null=True,
                              choices=(('FDE', 'fedex delivery exception'), ('I24', 'indiapost 24 hour'),('F24', 'fedex 24 hour'), ('FSI', 'fedex shipment information sent'), ('FLF', 'fedex local facility'),),
                              default=None)

    last_tracking_status = models.CharField(max_length=300, null=True, blank=True)
    
    last_tracking_status_timestamp=models.DateTimeField(blank=True, null=True)
    l=models.FloatField(default=0)
    b=models.FloatField(default=0)
    h=models.FloatField(default=0)
    actual_delivery_timestamp = models.DateTimeField(blank=True, null=True)
    estimated_delivery_timestamp = models.DateTimeField(blank=True, null=True)
    return_action=models.CharField(max_length=2,blank=True,null=True,
                              choices=(('R', 'Reshipped'),('RB','Returned to business')),
                              default=None)

    def __unicode__(self):
        return str(self.name)

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        self.__original_tracking_data = self.tracking_data

    def save(self, *args, **kwargs):
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        time = ind_time

        if self.mapped_tracking_no and (self.status == 'PU' or self.status == 'D' or self.status == 'P'):
            self.status = 'DI'
            self.update_time = time
            self.dispatch_time = time

        # whenever tracking data changes
        if self.tracking_data != self.__original_tracking_data:
            z = timezone('Asia/Kolkata')
            fmt = '%Y-%m-%d %H:%M:%S'
            ind_time = datetime.now(z)
            time = ind_time
            self.update_time = time
            if (self.last_tracking_status!=json.loads(self.tracking_data)[-1]['status']):
                self.last_tracking_status = json.loads(self.tracking_data)[-1]['status']
                self.last_tracking_status_timestamp=datetime.now(z)
            else:
                #now status hasnt changed
                try:
                    if self.last_tracking_status_timestamp:
                        hours=(datetime.datetime.now()-self.last_tracking_status_timestamp)//3600
                        if (hours>24 and ("local facility" in self.last_tracking_status.lower())):
                            self.warning_type='FLF'
                            self.warning=True
                except:
                    pass

            # Warnings rule definations
            if ('exception' in self.last_tracking_status.lower()):
                self.warning = True
                self.warning_type='FDE'
                self.qc_comment=self.qc_comment + self.last_tracking_status.lower()


        if not self.pk:
            z = timezone('Asia/Kolkata')
            fmt = '%Y-%m-%d %H:%M:%S'
            ind_time = datetime.now(z)
            time = ind_time
            self.date = ind_time
            time = str(time.replace(second=0, microsecond=0,tzinfo=None))
            self.update_time = ind_time
            self.tracking_data = "[{\"status\": \"Booking Received\", \"date\"	: \"" + time + " \", \"location\": \"Mumbai (Maharashtra)\"}]"
            super(Product, self).save(*args, **kwargs)
            alphabet = random.choice('BDQP')
            no1 = random.choice('1234567890')
            no2 = random.choice('1234567890')
            no = int(self.pk) + 134528
            trackingno = 'B' + str(no) + str(alphabet) + str(no1) + str(no2)
            self.real_tracking_no = trackingno

            kwargs['force_update'] = True
            kwargs['force_insert'] = False

        if (self.barcode is not None) and (len(self.barcode) > 12 or len(self.barcode) < 10):
            raise ValidationError("Barcode length should be 10")

        super(Product, self).save(*args, **kwargs)
        self.__original_tracking_data = self.tracking_data

class ProxyProduct(Product):
    class Meta:
        proxy = True



class RemittanceProductPending(Product):
    class Meta:
        proxy = True



class ExportOrder(Product):
    class Meta:
        proxy = True

class RemittanceProductComplete(Product):
    class Meta:
        proxy = True


class QcProduct(Product):
    class Meta:
        proxy = True


def send_update(sender, instance, created, **kwargs):

    # product can be pending complete returned picked up

    #                              choices=(('P', 'pending'), ('C', 'complete'), ('PU', 'pickedup'), ('CA', 'cancelled'), ('R', 'return')),

    #       ('P', 'pending'), ('C', 'complete'), ('N', 'cancelled'), ('D', 'in transit'), ('PU', 'pickedup')), default='P')

    # order will be pending intransit complete cancelled picked up

    products_in_order = Product.objects.filter(order=instance.order)

    if (instance.l and instance.b and instance.h):
        vol_weight= (instance.l *instance.b *instance.h)/5000
    else:
        vol_weight=None

    best_weight=max(instance.applied_weight,vol_weight)


    if best_weight:
        method = instance.order.method

        if (instance.order.payment_method == 'C'):
            cod_price1 = (1.5 / 100) * instance.price
            if (cod_price1 < 40):
                cod_price = 40
            else:
                cod_price = cod_price1

        else:
            cod_price = 0

        pincode = instance.order.pincode
        print pincode

        two_digits = pincode[:2]
        three_digits = pincode[:3]

        pricing = Pricing.objects.get(pk=instance.order.business.pk)

        if (method == 'N'):
            if (three_digits == '400'):
                price1 = pricing.normal_zone_a_0
                price2 = pricing.normal_zone_a_1
                price3 = pricing.normal_zone_a_2

            elif (two_digits == '41' or two_digits == '42' or two_digits == '43' or two_digits == '44' or three_digits == '403' or three_digits == '401' or two_digits == '36' or two_digits == '37' or two_digits == '38' or two_digits == '39'):
                price1 = pricing.normal_zone_b_0
                price2 = pricing.normal_zone_b_1
                price3 = pricing.normal_zone_b_2
            elif (two_digits == '56' or two_digits == '11' or three_digits == '600' or three_digits == '700'):
                price1 = pricing.normal_zone_c_0
                price2 = pricing.normal_zone_c_1
                price3 = pricing.normal_zone_c_2

            elif (two_digits == '78' or two_digits == '79' or two_digits == '18' or two_digits == '19'):
                price1 = pricing.normal_zone_e_0
                price2 = pricing.normal_zone_e_1
                price3 = pricing.normal_zone_e_2
            else:
                price1 = pricing.normal_zone_d_0
                price2 = pricing.normal_zone_d_1
                price3 = pricing.normal_zone_d_2

            if (best_weight <= 0.25):
                price = price1
            elif (best_weight <= 0.50):
                price = price2
            else:
                price = price2 + math.ceil((best_weight * 2 - 1)) * price3

        if (method == 'B'):
            if (three_digits == '400'):
                price1 = pricing.bulk_zone_a

            elif (
                                                        two_digits == '41' or two_digits == '42' or two_digits == '43' or two_digits == '44' or three_digits == '403' or two_digits == '36' or two_digits == '37' or two_digits == '38' or two_digits == '39'):
                price1 = pricing.bulk_zone_b
            elif (two_digits == '56' or two_digits == '11' or three_digits == '600' or three_digits == '700'):
                price1 = pricing.bulk_zone_c

            elif (two_digits == '78' or two_digits == '79' or two_digits == '18' or two_digits == '19'):
                price1 = pricing.bulk_zone_e
            else:
                price1 = pricing.bulk_zone_d

            if (best_weight <= 10):
                price = price1 * 10
            else:
                price = price1 * best_weight

        Order.objects.filter(pk=instance.order.pk).update(status='D')
        #        print "prrriiiceee"

        price = math.ceil(1.20 * price)

        Product.objects.filter(pk=instance.pk).update(shipping_cost=price, cod_cost=cod_price)
    #        print "Done"
    # MyModel.objects.filter(pk=some_value).update(field1='some value')
    #        print "in  loop"

    if instance.status == 'C' or instance.status == 'R':
        complete = True
        return_value = True
        other_case = False
        #		print "in complete loop"

        for product in products_in_order:
            if product.status != 'C':
                # print "false check"
                complete = False
            # print "1aaa"
            elif product.status != 'R':
                return_value = False
            # print "2aaa"
            elif (product.status != 'R' & product.status != 'C'):
                other_case = True
                #    print "3aaa"

        signals.post_save.disconnect(send_update_order, sender=Order)

        if (complete & (not return_value)):
            # print "am i here"
            # print "1111111111111111111111111111111111111111111111"
            instance.order.status = 'C'
            instance.order.save()

        elif ((not complete) & return_value):
            # print "222222222222222222222222222222222222222222222"
            # print "am i here"
            instance.order.status = 'R'
            instance.order.save()
        elif (other_case):
            pass
        else:
            # print "33333333333333333333333333333333333333333333	"
            instance.order.status = 'RC'
            instance.order.save()

        signals.post_save.connect(send_update_order, sender=Order)

    if (instance.status == 'PU') or (instance.status == 'CA'):
        # print "33333333333333333333333333333333333333333333	"
        pickedup = True
        for product in products_in_order:
            if (product.status != 'PU') & (product.status != 'CA'):
                pickedup = False

        if (pickedup):
            signals.post_save.disconnect(send_update_order, sender=Order)
            instance.order.status = 'PU'
            instance.order.save()
            signals.post_save.connect(send_update_order, sender=Order)

    if (instance.status == 'DI') or (instance.status == 'CA'):
        # print "33333333333333333333333333333333333333333333    "
        Dispatched = True
        for product in products_in_order:
            if (product.status != 'DI') & (product.status != 'CA'):
                Dispatched = False

        if (Dispatched):
            signals.post_save.disconnect(send_update_order, sender=Order)
            instance.order.status = 'DI'
            instance.order.save()
            signals.post_save.connect(send_update_order, sender=Order)

    if (instance.status == 'CA'):
        Cancelled = True
        for product in products_in_order:
            if (product.status != 'CA'):
                Cancelled = False
        if (Cancelled):
            # signals.post_save.disconnect(send_update_order, sender=Order)
            signals.post_save.disconnect(send_update_order, sender=Order)
            instance.order.status = 'N'
            instance.order.save()
            signals.post_save.connect(send_update_order, sender=Order)


post_save.connect(send_update, sender=Product)


# to change cost on product when order is saved


def send_update_order(sender, instance, created, **kwargs):
    # product can be pending complete returned picked up

    #                              choices=(('P', 'pending'), ('C', 'complete'), ('PU', 'pickedup'), ('CA', 'cancelled'), ('R', 'return')),

    #       ('P', 'pending'), ('C', 'complete'), ('N', 'cancelled'), ('D', 'in transit'), ('PU', 'pickedup')), default='P')

    # order will be pending intransit complete cancelled picked up

    products = Product.objects.filter(order=instance)

    if instance.status == 'C' or instance.status == 'PU' or instance.status == 'CA' or instance.status == 'P' or instance.status == 'R':
        signals.post_save.disconnect(send_update, sender=Product)
        for product in products:
            product.status = instance.status
            product.save()

        signals.post_save.connect(send_update, sender=Product)

    for product in products:

        if (product.l and product.b and product.h):
            vol_weight= (product.l *product.b *product.h)/5000
        else:
            vol_weight=None

        best_weight=max(product.applied_weight,vol_weight)

        if best_weight:
            method = instance.method

            if (instance.payment_method == 'C'):
                cod_price1 = (1.5 / 100) * product.price
                if (cod_price1 < 40):
                    cod_price = 40
                else:
                    cod_price = cod_price1

            else:
                cod_price = 0

            pincode = instance.pincode
            print pincode

            two_digits = pincode[:2]
            three_digits = pincode[:3]

            pricing = Pricing.objects.get(pk=instance.business.pk)
            print "methhhhhhhoooooooooooood"
            print method
            if (method == 'N'):
                if (three_digits == '400'):
                    price1 = pricing.normal_zone_a_0
                    price2 = pricing.normal_zone_a_1
                    price3 = pricing.normal_zone_a_2

                elif (two_digits == '41' or two_digits == '42' or two_digits == '43' or two_digits == '44' or three_digits == '403' or three_digits == '401' or two_digits == '36' or two_digits == '37' or two_digits == '38' or two_digits == '39'):
                    price1 = pricing.normal_zone_b_0
                    price2 = pricing.normal_zone_b_1
                    price3 = pricing.normal_zone_b_2
                elif (two_digits == '56' or two_digits == '11' or three_digits == '600' or three_digits == '700'):
                    price1 = pricing.normal_zone_c_0
                    price2 = pricing.normal_zone_c_1
                    price3 = pricing.normal_zone_c_2

                elif (two_digits == '78' or two_digits == '79' or two_digits == '18' or two_digits == '19'):
                    price1 = pricing.normal_zone_e_0
                    price2 = pricing.normal_zone_e_1
                    price3 = pricing.normal_zone_e_2
                else:
                    price1 = pricing.normal_zone_d_0
                    price2 = pricing.normal_zone_d_1
                    price3 = pricing.normal_zone_d_2

                if (best_weight <= 0.25):
                    price = price1
                elif (best_weight <= 0.50):
                    price = price2
                else:
                    price = price2 + math.ceil((best_weight * 2 - 1)) * price3

            if (method == 'B'):
                if (three_digits == '400'):
                    price1 = pricing.bulk_zone_a

                elif (
                                                            two_digits == '41' or two_digits == '42' or two_digits == '43' or two_digits == '44' or three_digits == '403' or two_digits == '36' or two_digits == '37' or two_digits == '38' or two_digits == '39'):
                    price1 = pricing.bulk_zone_b
                elif (two_digits == '56' or two_digits == '11' or three_digits == '600' or three_digits == '700'):
                    price1 = pricing.bulk_zone_c

                elif (two_digits == '78' or two_digits == '79' or two_digits == '18' or two_digits == '19'):
                    price1 = pricing.bulk_zone_e
                else:
                    price1 = pricing.bulk_zone_d

                if (best_weight <= 10):
                    price = price1 * 10
                else:
                    price = price1 * best_weight

            # print "prrriiiceee"

            price = math.ceil(1.20 * price)
            signals.post_save.disconnect(send_update, sender=Product)

            product.shipping_cost = price
            product.cod_cost = cod_price
            product.save()
            signals.post_save.connect(send_update, sender=Product)


post_save.connect(send_update_order, sender=Order)


class Billing(models.Model):
    id = models.AutoField(primary_key=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    business = models.ForeignKey(Business, related_name='bills', null=True, blank=True)
    orders = models.ManyToManyField(Order, related_name='bill', null=True, blank=True)
    total_shipping_cost = models.FloatField(default=0.0)
    total_cod_remittance_eligible = models.FloatField(default=0.0)
    total_cod_remittance_pending = models.FloatField(default=0.0)
    service_tax = models.FloatField(default=0.0)
    discounts = models.FloatField(default=0.0)
    carryover_balance = models.FloatField(default=0.0)
    balance_due = models.FloatField(default=0.0)
    due_date = models.DateField(blank=True, null=True)


class Payment(models.Model):
    amount = models.FloatField(default=0.0)
    payment_time = models.DateTimeField(blank=True, null=True)
    method = models.CharField(max_length=100, null=True, blank=True)
    business = models.ForeignKey(Business)
    bill = models.ForeignKey(Billing, related_name='payments', null=True, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.pk:
            z = timezone('Asia/Kolkata')
            fmt = '%Y-%m-%d %H:%M:%S'
            ind_time = datetime.now(z)
            self.payment_time = ind_time.strftime(fmt)
        super(Payment, self).save(*args, **kwargs)


class X(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)


class Usernamecheck(models.Model):
    username = models.CharField(max_length=100, null=True, blank=True)
    exist = models.CharField(max_length=1,
                             choices=(('Y', 'yes'), ('N', 'no'),),
                             default='N')


class Pincodecheck(models.Model):
    pincode = models.CharField(max_length=6)

    def __unicode__(self):
        return str(self.pincode)


class Pricing(models.Model):
    business = models.OneToOneField(Business, primary_key=True)
    normal_zone_a_0 = models.FloatField(default=15)
    normal_zone_a_1 = models.FloatField(default=15)
    normal_zone_a_2 = models.FloatField(default=13)
    normal_zone_b_0 = models.FloatField(default=20)
    normal_zone_b_1 = models.FloatField(default=30)
    normal_zone_b_2 = models.FloatField(default=26)
    normal_zone_c_0 = models.FloatField(default=25)
    normal_zone_c_1 = models.FloatField(default=33)
    normal_zone_c_2 = models.FloatField(default=32)
    normal_zone_d_0 = models.FloatField(default=30)
    normal_zone_d_1 = models.FloatField(default=40)
    normal_zone_d_2 = models.FloatField(default=38)
    normal_zone_e_0 = models.FloatField(default=38)
    normal_zone_e_1 = models.FloatField(default=48)
    normal_zone_e_2 = models.FloatField(default=45)
    bulk_zone_a = models.FloatField(default=8)
    bulk_zone_b = models.FloatField(default=9.5)
    bulk_zone_c = models.FloatField(default=11)
    bulk_zone_d = models.FloatField(default=13)
    bulk_zone_e = models.FloatField(default=15)

    def __unicode__(self):
        return str(self.business)


class Weight(models.Model):
    weight = models.FloatField(primary_key=True)

    def __unicode__(self):
        return str(self.weight)


class Zone(models.Model):
    zone = models.CharField(max_length=2, primary_key=True)

    def __unicode__(self):
        return str(self.zone)


class Pricing2(models.Model):
    business = models.ForeignKey(Business,related_name='pricing2s')
    weight = models.ForeignKey(Weight)
    zone = models.ForeignKey(Zone)
    type = models.CharField(max_length=1,
                            choices=(('N', 'normal'), ('B', 'bulk'),),
                            default='N')
    price = models.FloatField(default=15)
    ppkg = models.FloatField(default=15)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if self.weight.weight==11.0:
            self.price=self.ppkg*11
        else:
            self.ppkg = self.price / self.weight.weight

        if not self.pk:
            if Pricing2.objects.filter(zone__zone=self.zone.zone,weight__weight=self.weight.weight,type=self.type,business=self.business).count() > 0:
                raise ValidationError("Pricing already exists")
        
        super(Pricing2, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.business)


class Forgotpass(models.Model):
    business = models.ForeignKey(Business)
    auth = models.CharField(max_length=80, null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        if not self.pk:
            self.time = ind_time.strftime(fmt)
        super(Forgotpass, self).save(*args, **kwargs)


class Changepass(models.Model):
    business = models.ForeignKey(Business)
    changed = models.CharField(max_length=1,
                               choices=(('Y', 'yes'), ('N', 'no'),),
                               default='N')
    time = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        if not self.pk:
            self.time = ind_time.strftime(fmt)
        super(Changepass, self).save(*args, **kwargs)


class Barcode(models.Model):
    created_at = models.DateTimeField(
        verbose_name='created at',
        auto_now_add=True
    )
    value = models.CharField(null=True, blank=True, default=None, max_length=12, unique=True)
    business = models.ForeignKey(Business, related_name="alloted_barcodes")

    def save(self, *args, **kwargs):
        if (self.value is not None) and (len(self.value) > 12 or len(self.value) < 10):
            raise ValidationError("Barcode length should be 10")

        super(Barcode, self).save(*args, **kwargs)


def add_pricing(sender, instance, created, **kwargs):
    if instance.pricing2s.count()==0:
        ndict = {'a': [(0.25,15), (0.5,15), (1,28), (1.5,41),(2,54), (2.5,67), (3,80), (3.5,93), (4,106), (4.5,119), (5,132), (5.5,145),(6,158), (6.5,171), (7,184),(7.5,197), (8,210), (8.5,223), (9,236),(9.5,249), (10,262), (11,286)],
                 'b': [(0.25,20), (0.5,30), (1,56), (1.5,82),(2,108), (2.5,134), (3,160), (3.5,186),(4,212),(4.5,238), (5,264), (5.5,290),(6,316), (6.5,342),(7,368),(7.5,394), (8,420), (8.5,446),(9,472),(9.5,498), (10,524), (11,572)],
                 'c': [(0.25,25), (0.5,33), (1,65), (1.5,97),(2,129), (2.5,161), (3,193), (3.5,225),(4,257),(4.5,289), (5,321), (5.5,353),(6,385), (6.5,417),(7,449),(7.5,481), (8,513), (8.5,545),(9,577),(9.5,609), (10,641), (11,704)],
                 'd': [(0.25,30), (0.5,40), (1,78), (1.5,116),(2,154), (2.5,192), (3,230),(3.5,268), (4,306),(4.5,344), (5,382),(5.5,420), (6,458),(6.5,496), (7,534),(7.5,572), (8,610), (8.5,648),(9,686),(9.5,724), (10,762), (11,836)],
                 'e': [(0.25,38), (0.5,48), (1,93), (1.5,138),(2,183), (2.5,228), (3,273),(3.5,318), (4,363),(4.5,408), (5,453),(5.5,498), (6,543),(6.5,588), (7,633),(7.5,678), (8,723),(8.5,768), (9,813),(9.5,858), (10,903), (11,990)],
                 }

        bdict = {'a': [(1,80),(2,80), (3,80), (4,80), (5,80), (6,80), (7,80), (8,80), (9,80), (10,80) , (11,88)],
                 'b': [(1,95),(2,95), (3,95), (4,95), (5,95), (6,95), (7,95), (8,95), (9,95), (10,95) , (11,104.5)],
                 'c': [(1,110),(2,110), (3,110), (4,110), (5,110), (6,110), (7,110), (8,110), (9,110), (10,110), (11,121)],
                 'd': [(1,130),(2,130), (3,130), (4,130), (5,130), (6,130), (7,130), (8,130), (9,130), (10,130), (11,143)],
                 'e': [(1,150),(2,150), (3,150), (4,150), (5,150), (6,150), (7,150), (8,150), (9,150), (10,150), (11,165)]}

        for key in ndict:
            for w in ndict[key]:
                zone = Zone.objects.get(zone=key)
                weight = Weight.objects.get(weight=w[0])
                p=Pricing2(business=instance,zone=zone,weight=weight,price=w[1],type='N')
                p.save()

        for key in bdict:
            for w in bdict[key]:
                zone = Zone.objects.get(zone=key)
                weight = Weight.objects.get(weight=w[0])
                p=Pricing2(business=instance,zone=zone,weight=weight,price=w[1],type='B')
                p.save()


        price=[20,40]

        pricingquerset=Pricing2.objects.filter(business=instance,type='N')
        for p in pricingquerset:
            if p.zone.zone=='a':
                p.price=price[0]*round(p.weight.weight/0.5)
                p.save()
            else:
                p.price=price[1]*round(p.weight.weight/0.5)
                p.save()

        price=[8,12]
        pricingquerset=Pricing2.objects.filter(business=instance,type='B')
        for p in pricingquerset:
            if p.zone.zone=='a':
                p.price=price[0]*round(p.weight.weight)
                p.save()
            else:
                p.price=price[1]*round(p.weight.weight)
                p.save()



post_save.connect(add_pricing, sender=Business)
