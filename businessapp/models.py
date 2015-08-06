from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
# from django.contrib.auth.models import User
from datetime import datetime
from pytz import timezone
from django.db.models.signals import post_save
import hashlib
import random
# Create your models here.
import math
from django.contrib.auth.models import User

from django.db.models import signals


class Profile(models.Model):
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=100)
    usertype = models.CharField(max_length=1, choices=(('O', 'ops'), ('B', 'bd'), ('A', 'admin'),),
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


class Business(models.Model):
    # phone_regex = RegexValidator(regex=r'^[0-9]*$', message="Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")
    username = models.CharField(max_length=20, primary_key=True)
    apikey = models.CharField(max_length=100, null=True, blank=True)
    business_name = models.CharField(max_length=100)
    password = models.CharField(max_length=300)
    email = models.EmailField(max_length=75)
    name = models.CharField(max_length=100)
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
    #key=models.CharField(max_length = 100,null=True,blank =True)
    businessmanager = models.ForeignKey(Profile, null=True, blank=True)
    show_tracking_company = models.CharField(max_length=1, choices=(('Y', 'yes'), ('N', 'no'),), null=True, blank=True,
                                             default='N')
    pb = models.ForeignKey(PBUser, null=True, blank=True)
    assigned_pickup_time = models.TimeField(null=True, blank=True, default=datetime.now())
    #     # Use UserManager to get the create_user method, etc.
    #     objects = UserManager()

    def save(self, *args, **kwargs):
        #print self.tracking_no
        #print self.pk
        #print "jkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkj"
        if not self.apikey:
            print "wkwkwkwkwkwkwkwkwk"
            self.apikey = hashlib.sha1(str(random.getrandbits(256))).hexdigest();
        super(Business, self).save(*args, **kwargs)


    def __unicode__(self):
        return str(self.business_name)


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
    order_no = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=12)
    email = models.EmailField(max_length=75, null=True, blank=True)
    #address=models.CharField(max_length = 300)
    #flat_no=models.CharField(max_length = 100,null=True,blank =True)
    address1 = models.CharField(max_length=300, null=True, blank=True)
    address2 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=30, null=True, blank=True)
    country = models.CharField(max_length=30, null=True, blank=True)
    payment_method = models.CharField(max_length=1, choices=(('F', 'free checkout'), ('C', 'cod'),), )
    book_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=(
        ('P', 'pending'), ('C', 'complete'), ('N', 'cancelled'), ('D', 'in transit'), ('PU', 'pickedup'),
        ('RC', 'return/completed'), ('R', 'return')), default='P')

    method = models.CharField(max_length=1,
                              choices=(('B', 'Bulk'), ('N', 'Normal'),),
                              blank=True, null=True)
    business = models.ForeignKey(Business)


    def __unicode__(self):
        return str(self.order_no)


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        z = timezone('Asia/Kolkata')
        fmt = '%Y-%m-%d %H:%M:%S'
        ind_time = datetime.now(z)
        if not self.pk:
            self.book_time = ind_time.strftime(fmt)
        super(Order, self).save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.IntegerField(max_length=10, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    price = models.IntegerField(max_length=10, null=True, blank=True)
    weight = models.FloatField(max_length=10, null=True, blank=True)
    applied_weight = models.FloatField(max_length=10, null=True, blank=True)
    order = models.ForeignKey(Order, null=True, blank=True)
    real_tracking_no = models.CharField(max_length=10, blank=True, null=True)
    mapped_tracking_no = models.CharField(max_length=50, null=True, blank=True)
    tracking_data = models.CharField(max_length=8000, null=True, blank=True)
    kartrocket_order = models.CharField(max_length=100, null=True, blank=True)
    company = models.CharField(max_length=2,
                               choices=[('F', 'FedEx'), ('D', 'Delhivery'), ('P', 'Professional'), ('G', 'Gati'),
                                        ('A', 'Aramex'), ('E', 'Ecomexpress'), ('DT', 'dtdc'), ('FF', 'First Flight'),
                                        ('M', 'Maruti courier'), ('I', 'India Post'), ('S', 'Sendd')],
                               blank=True, null=True)
    shipping_cost = models.IntegerField(null=True, blank=True)
    cod_cost = models.IntegerField(default=0, null=True, blank=True)
    return_cost = models.IntegerField(default=0, null=True, blank=True)

    #tracking_no=models.AutoField(primary_key=True)
    barcode = models.CharField(null=True, blank=True, default=None, max_length=12, unique=True)
    status = models.CharField(max_length=2,
                              choices=(('P', 'pending'), ('C', 'complete'), ('PU', 'pickedup'), ('CA', 'cancelled'),
                                       ('R', 'return')),
                              default='P')

    date = models.DateTimeField(null=True, blank=True)
    remittance = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if (self.barcode is not None) and (len(self.barcode) > 12 or len(self.barcode) < 10):
            raise ValidationError("Barcode length should be 10")
        if not self.pk:
            print self.pk
            z = timezone('Asia/Kolkata')
            fmt = '%Y-%m-%d %H:%M:%S'
            ind_time = datetime.now(z)
            time = ind_time.strftime(fmt)
            self.date = ind_time.strftime(fmt)
            time = str(time)
            self.tracking_data = "[{\"status\": \"Booking Received\", \"date\"	: \"" + time + " \", \"location\": \"Mumbai (Maharashtra)\"}]"
            print self.tracking_data
            #print self.status
            super(Product, self).save(*args, **kwargs)
            print self.pk
            alphabet = random.choice('BDQP')
            no1 = random.choice('1234567890')
            no2 = random.choice('1234567890')
            no = int(self.pk) + 134528
            trackingno = 'B' + str(no) + str(alphabet) + str(no1) + str(no2)
            print trackingno
            self.real_tracking_no = trackingno
            #p = Pricing.objects.create(amount_charged_by_courier=0, amount_spent_in_packingpickup=0,amount_paid=0)
            #self.pricing=p
            kwargs['force_update'] = True
            kwargs['force_insert'] = False

            print "H"
        super(Product, self).save(*args, **kwargs)
        print "L"


class RemittanceProduct(Product):
    class Meta:
        proxy = True

def send_update(sender, instance, created, **kwargs):
    # product can be pending complete returned picked up

    #                              choices=(('P', 'pending'), ('C', 'complete'), ('PU', 'pickedup'), ('CA', 'cancelled'), ('R', 'return')),

    #       ('P', 'pending'), ('C', 'complete'), ('N', 'cancelled'), ('D', 'in transit'), ('PU', 'pickedup')), default='P')

    # order will be pending intransit complete cancelled picked up



    if instance.applied_weight:
        print instance.order.business.pk
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

            elif (
                                                        two_digits == '41' or two_digits == '42' or two_digits == '43' or two_digits == '44' or three_digits == '403' or two_digits == '36' or two_digits == '37' or two_digits == '38' or two_digits == '39'):
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

            if (instance.applied_weight <= 0.25):
                price = price1
            elif (instance.applied_weight <= 0.50):
                price = price2
            else:
                price = price2 + math.ceil((instance.applied_weight * 2 - 1)) * price3

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

            if (instance.applied_weight <= 10):
                price = price1 * 10
            else:
                price = price1 * instance.applied_weight

        Order.objects.filter(pk=instance.order.pk).update(status='D')
#        print "prrriiiceee"

        price = math.ceil(1.20 * price)

        Product.objects.filter(pk=instance.pk).update(shipping_cost=price, cod_cost=cod_price)
#        print "Done"
        #MyModel.objects.filter(pk=some_value).update(field1='some value')
#        print "in  loop"

    if instance.status == 'C' or instance.status == 'R':
        complete = True
        return_value = True
        other_case = False
        #		print "in complete loop"

        products_in_order = Product.objects.filter(order=instance.order)
        print "count"
        print products_in_order.count()
        for product in products_in_order:
            if product.status != 'C':
                #print "false check"
                complete = False

            elif product.status != 'R':
                return_value = False
            elif (product.status != 'R' & product.status != 'C'):
                other_case = True

        if (complete & (not return_value)):
            #print "am i here"
            #print "1111111111111111111111111111111111111111111111"
            instance.order.status = 'C'
            instance.order.save()

        elif ((not complete) & return_value):
            #print "222222222222222222222222222222222222222222222"
            #print "am i here"
            instance.order.status = 'R'
            instance.order.save()
        elif (other_case):
            pass
        else:
            #print "33333333333333333333333333333333333333333333	"
            instance.order.status = 'RC'
            instance.order.save()



    if (instance.status == 'PU') or (instance.status == 'CA'):
    	print "33333333333333333333333333333333333333333333	"
    	pickedup = True
    	products_in_order = Product.objects.filter(order=instance.order)
        for product in products_in_order:
        	if (product.status!='PU') & (product.status!='CA'):
        		pickedup=False 

        if (pickedup):
        	instance.order.status = 'PU'
        	instance.order.save()


post_save.connect(send_update, sender=Product)


# to change cost on product when order is saved


def send_update_order(sender, instance, created, **kwargs):
    # product can be pending complete returned picked up

    #                              choices=(('P', 'pending'), ('C', 'complete'), ('PU', 'pickedup'), ('CA', 'cancelled'), ('R', 'return')),

    #       ('P', 'pending'), ('C', 'complete'), ('N', 'cancelled'), ('D', 'in transit'), ('PU', 'pickedup')), default='P')

    # order will be pending intransit complete cancelled picked up



    if instance.status=='C' or instance.status=='PU' or instance.status=='CA' or instance.status=='P' or instance.status=='R':
    	products=Product.objects.filter(order=instance)
    	signals.post_save.disconnect(send_update, sender=Product)
    	for product in products:
    		product.status= instance.status
    		product.save()

    	signals.post_save.connect(send_update, sender=Product)


    products=Product.objects.filter(order=instance)
    for product in products:
    	print "look here for products"
    	print product.applied_weight

        if product.applied_weight:
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

	            elif (
	                                                        two_digits == '41' or two_digits == '42' or two_digits == '43' or two_digits == '44' or three_digits == '403' or two_digits == '36' or two_digits == '37' or two_digits == '38' or two_digits == '39'):
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

	            if (product.applied_weight <= 0.25):
	                price = price1
	            elif (product.applied_weight <= 0.50):
	                price = price2
	            else:
	                price = price2 + math.ceil((product.applied_weight * 2 - 1)) * price3

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

	            if (product.applied_weight <= 10):
	                price = price1 * 10
	            else:
	                price = price1 * product.applied_weight

#        print "prrriiiceee"

        	price = math.ceil(1.20 * price)

        	Product.objects.filter(pk=product.pk).update(shipping_cost=price, cod_cost=cod_price)

post_save.connect(send_update_order, sender=Order)


class Payment(models.Model):
    amount = models.IntegerField()
    payment_time = models.DateTimeField(null=True, blank=True)
    method = models.CharField(max_length=100, null=True, blank=True)
    business = models.ForeignKey(Business)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.pk:
            z = timezone('Asia/Kolkata')
            fmt = '%Y-%m-%d %H:%M:%S'
            ind_time = datetime.now(z)
            self.payment_time = ind_time.strftime(fmt)
        super(Payment, self).save(*args, **kwargs)


class Billing(models.Model):
    business = models.ForeignKey(Business, null=True, blank=True)


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