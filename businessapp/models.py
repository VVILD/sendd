from django.db import models
#from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import datetime,timedelta
from pytz import timezone
import pytz

import random
# Create your models here.

from django.contrib.auth.models import User, UserManager

class BusinessManager(User):
    """User with app settings."""
    Phone = models.CharField(max_length=50)

    # Use UserManager to get the create_user method, etc.
    objects = UserManager()

class Business(models.Model):
	#phone_regex = RegexValidator(regex=r'^[0-9]*$', message="Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")
	username=models.CharField(max_length = 20,primary_key=True)
	business_name = models.CharField(max_length = 100)
	password=models.CharField(max_length = 300)
	email = models.EmailField(max_length = 75)	
	name = models.CharField(max_length = 100)
	contact_mob = models.CharField(max_length = 15)
	contact_office= models.CharField(max_length = 15,null=True,blank =True)
	pickup_time=models.CharField(max_length=1,choices=(('M','morning') ,('N','noon'),('E','evening'),),null=True,blank =True)
	address=models.CharField(max_length = 315,null=True,blank =True)
	city=models.CharField(max_length = 50,null=True,blank =True)
	state=models.CharField(max_length = 50,null=True,blank =True)
	pincode=models.CharField(max_length = 50,null=True,blank =True)
	company_name = models.CharField(max_length = 100,null=True,blank =True)
	website =models.CharField(max_length = 100,null=True,blank =True)
	#key=models.CharField(max_length = 100,null=True,blank =True)
	businessmanager=models.ForeignKey(User,null=True,blank =True) 
	

	def __unicode__(self):
		return str(self.username)	

class LoginSession(models.Model):
	Business=models.ForeignKey(Business,null=True,blank=True)
	time=models.DateTimeField(null=True,blank=True)
	msg=models.CharField(max_length=100,
									  choices=(('notregistered','notregistered') ,('wrongpassword','wrongpassword'),('success','success'),),
									  default='wrongpassword')

	def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		z=timezone('Asia/Kolkata')
		fmt='%Y-%m-%d %H:%M:%S'
		ind_time=datetime.now(z)
		if not self.pk:
			self.time = ind_time.strftime(fmt)
		super(LoginSession, self).save(*args, **kwargs)


class Order(models.Model):
	order_no=models.AutoField(primary_key=True)
	name = models.CharField(max_length = 100,null=True,blank =True)
	phone = models.CharField(max_length = 12)
	#email = models.EmailField(max_length = 75,null=True,blank =True)
	#address=models.CharField(max_length = 300)
	#flat_no=models.CharField(max_length = 100,null=True,blank =True)
	street_address=models.CharField(max_length = 300,null=True,blank =True)
	city=models.CharField(max_length = 50,null=True,blank =True)
	state=models.CharField(max_length = 50,null=True,blank =True)
	pincode=models.CharField(max_length =30,null=True,blank =True)
	country=models.CharField(max_length =30,null=True,blank =True)
	payment_method=models.CharField(max_length=1,choices=(('F','free checkout') ,('C','cod'),),)
	book_time=models.DateTimeField(null=True,blank=True)
	status=models.CharField(max_length=1,choices=(('P','pending') ,('C','complete'),('N','cancelled'),('D','delivered'),),default='P')
	business=models.ForeignKey(Business)


	def __unicode__(self):
		return str(self.order_no)

	def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		z=timezone('Asia/Kolkata')
		fmt='%Y-%m-%d %H:%M:%S'
		ind_time=datetime.now(z)
		if not self.pk:
			self.book_time = ind_time.strftime(fmt)
		super(Order, self).save(*args, **kwargs)

class Product(models.Model):
	name = models.CharField(max_length = 100,null=True,blank =True)
	price = models.CharField(max_length = 10,null=True,blank =True)
	weight = models.CharField(max_length = 10,null=True,blank =True)
	order=models.ForeignKey(Order,null=True,blank =True)
	real_tracking_no=models.CharField(max_length=10,blank=True,null=True)
	mapped_tracking_no=models.CharField(max_length = 50,null=True,blank=True)
	tracking_data=models.CharField(max_length = 8000,null=True,blank=True)
	company=models.CharField(max_length=1,
									  choices=(('F','FedEx') ,('D','Delhivery'),),
									  blank=True , null = True)
	shipping_cost=models.IntegerField(null=True,blank=True)

	def save(self, *args, **kwargs):
		#print self.tracking_no
		#print self.pk
		#print "jkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkjjkjkjkjkjkkjkjkjkj"
		if not self.pk:
			print self.pk
			z=timezone('Asia/Kolkata')
			fmt='%Y-%m-%d %H:%M:%S'
			ind_time=datetime.now(z)
			time = ind_time.strftime(fmt)
			time=str(time)
			self.tracking_data = "[{\"status\": \"Booking Received\", \"date\"	: \"" +time+" \", \"location\": \"Mumbai (Maharashtra)\"}]"
			print self.tracking_data
			#print self.status
			super(Product, self).save(*args, **kwargs)
			print self.pk
			alphabet=random.choice('BDQP')
			no1=random.choice('1234567890')
			no2=random.choice('1234567890')
			no=int(self.pk)+ 134528
			trackingno='S'+str(no) + str(alphabet)+str(no1)+str(no2)
			print trackingno
			self.real_tracking_no=trackingno
			#p = Pricing.objects.create(amount_charged_by_courier=0, amount_spent_in_packingpickup=0,amount_paid=0)
			#self.pricing=p
			kwargs['force_update'] = True
			kwargs['force_insert'] = False
			
			print "H"
		super(Product, self).save(*args, **kwargs)
		print "L"


class Payment(models.Model):
	amount= models.IntegerField()
	payment_time=models.DateTimeField(null=True,blank=True)
	method=models.CharField(max_length=100,null=True,blank=True)
	business=models.ForeignKey(Business)

	def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		if not self.pk:
			z=timezone('Asia/Kolkata')
			fmt='%Y-%m-%d %H:%M:%S'
			ind_time=datetime.now(z)
			self.payment_time = ind_time.strftime(fmt)
		super(Order, self).save(*args, **kwargs)
	

class X(models.Model):
	name=models.CharField(max_length=100,null=True,blank=True)



class Usernamecheck(models.Model):
	username=models.CharField(max_length=100,null=True,blank=True)
	exist=models.CharField(max_length=1,
									  choices=(('Y','yes') ,('N','no'),),
									  default='N')