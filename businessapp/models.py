from django.db import models
#from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import datetime,timedelta
from pytz import timezone
import pytz

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
	mob = models.CharField(max_length = 12,null=True,blank =True)
	office= models.CharField(max_length = 15,null=True,blank =True)
	name = models.CharField(max_length = 100,null=True,blank =True)
	password=models.CharField(max_length = 300,null=True,blank =True)
	email = models.EmailField(max_length = 75,null=True,blank =True)
	
	time=models.DateTimeField(null=True,blank=True)
	businessmanager=models.ForeignKey(User) 
	pickup_time=models.CharField(max_length=1,choices=(('M','morning') ,('N','noon'),('E','evening'),),)

	def save(self, *args, **kwargs):
		if not self.pk:
			z=timezone('Asia/Kolkata')
			fmt='%Y-%m-%d %H:%M:%S'
			ind_time=datetime.now(z)
			self.time = ind_time.strftime(fmt)
			super(Business, self).save(*args, **kwargs)


	def __unicode__(self):
		return str(self.phone)	


class Order(models.Model):
	order_no=models.AutoField(primary_key=True)
	name = models.CharField(max_length = 100,null=True,blank =True)
	phone = models.CharField(max_length = 12)
	email = models.EmailField(max_length = 75,null=True,blank =True)
	address=models.CharField(max_length = 300)
	payment_method=models.CharField(max_length=1,choices=(('F','free checkout') ,('C','cod'),),)
	date=models.DateField(null=True,blank =True)
	time=models.TimeField(null=True,blank =True)
	book_time=models.DateTimeField(null=True,blank=True)
	status=models.CharField(max_length=1,choices=(('P','pending') ,('C','complete'),('N','cancelled'),('D','delivered'),),)



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
	order=models.ForeignKey(Order)


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
	

