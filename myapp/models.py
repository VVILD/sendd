from django.db import models
from django.core.validators import RegexValidator
import hashlib
from datetime import datetime,timedelta
from pytz import timezone
import pytz
import random


class User(models.Model):
	phone_regex = RegexValidator(regex=r'^[0-9]*$', message="Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")
	phone = models.CharField(validators=[phone_regex],max_length = 12,primary_key=True)
	name = models.CharField(max_length = 100)
	password=models.CharField(max_length = 300)
	email = models.EmailField(max_length = 75,null=True,blank =True)
	otp=models.IntegerField(null=True,blank=True)
	apikey= models.CharField(max_length = 100,null=True,blank=True)
	referral_code= models.CharField(max_length = 50,null=True,blank=True)
	time=models.DateTimeField(null=True,blank=True)

	def save(self, *args, **kwargs):
		if self.password:
			salt='crawLINGINmySKin'
			hsh = hashlib.sha224(self.password+salt).hexdigest()
			self.password=hsh
			z=timezone('Asia/Kolkata')
			fmt='%Y-%m-%d %H:%M:%S'
			ind_time=datetime.now(z)
			self.time = ind_time.strftime(fmt)
		super(User, self).save(*args, **kwargs)


	def __unicode__(self):
		return str(self.name)+ '|' +str(self.phone)

class Address(models.Model):
	flat_no=models.CharField(max_length = 100)
	locality=models.CharField(max_length = 200)
	city=models.CharField(max_length = 50)
	state=models.CharField(max_length = 50)
	pincode=models.CharField(max_length =30)
	country=models.CharField(max_length =30)
	def __unicode__(self):
		return str(self.flat_no) + ',' + str(self.locality) + ',' + str(self.city) + ',' +str(self.state) +'-' +str(self.pincode)  

class Order(models.Model):
	order_no=models.AutoField(primary_key=True)
	date=models.DateField(null=True,blank =True)
	time=models.TimeField(null=True,blank =True)
	user=models.ForeignKey(User)
	status=models.CharField(max_length=1,
									  choices=(('P','pending') ,('C','complete'),),
									  default='P')
	cost=models.CharField(max_length = 10,null=True ,blank=True)
	paid=models.CharField(max_length=1,
									  choices=(('Y','yes') ,('N','no'),),
									  blank=True , null = True)

	cancelled=models.CharField(max_length=1,
									  choices=(('Y','yes') ,('N','no'),),
									  default='N')

	latitude = models.DecimalField(max_digits=25, decimal_places=20,null=True ,blank=True)
	longitude = models.DecimalField(max_digits=25, decimal_places=20,null=True ,blank=True)
	address=models.CharField(max_length = 200,null=True ,blank=True)
	pincode=models.CharField(max_length =30,null=True ,blank=True)
	flat_no=models.CharField(max_length =100,null=True ,blank=True)
	picked_up=models.BooleanField(default=False)

	def __unicode__(self):
		return str(self.order_no)



class Shipment(models.Model):
	weight=models.CharField(max_length=10,null=True,blank=True)
	price=models.CharField(max_length=10,null=True,blank=True)
	name=models.CharField(max_length=50,null=True,blank=True)
	tracking_no=models.AutoField(primary_key=True)
	real_tracking_no=models.CharField(max_length=10,blank=True,null=True)
	mapped_tracking_no=models.CharField(max_length = 50,null=True,blank=True)
	tracking_data=models.CharField(max_length = 8000,null=True,blank=True)
	img=models.ImageField(upload_to = 'shipment/')	
	category=models.CharField(max_length=1,
									  choices=(('P','premium') ,('S','standard'),('E','economy'),),
									  blank=True , null = True)
	drop_name=models.CharField(max_length = 100,null=True)
	phone_regex = RegexValidator(regex=r'^[0-9]*$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	drop_phone = models.CharField(validators=[phone_regex],max_length =12,null=True)
	drop_address=models.ForeignKey(Address,null=True)
	order=models.ForeignKey(Order,null=True)
	status=models.CharField(max_length=1,
									  choices=(('P','pending') ,('C','complete'),),
									  default='P')
	paid=models.CharField(max_length=10,
									  choices=(('Paid','Paid') ,('Not Paid','Not Paid'),),
									  blank=True , null = True ,default='Not Paid')
	company=models.CharField(max_length=1,
									  choices=(('F','FedEx') ,('D','Delhivery'),),
									  blank=True , null = True)
	
	def save(self, *args, **kwargs):
		print self.tracking_no
		print self.pk
		if not self.pk:
			print self.pk
			z=timezone('Asia/Kolkata')
			fmt='%Y-%m-%d %H:%M:%S'
			ind_time=datetime.now(z)
			time = ind_time.strftime(fmt)
			time=str(time)
			self.tracking_data = "[{\"status\": \"Booking Received\", \"date\"	: \"" +time+" \", \"location\": \"Mumbai (Maharashtra)\"}]"
			print self.tracking_data
			print self.status
			super(Shipment, self).save(*args, **kwargs)
			print self.pk
			alphabet=random.choice('BDQP')
			no1=random.choice('1234567890')
			no2=random.choice('1234567890')
			no=int(self.pk)+ 134528
			trackingno='S'+str(no) + str(alphabet)+str(no1)+str(no2)
			print trackingno
			self.real_tracking_no=trackingno
		super(Shipment, self).save(*args, **kwargs)
			

class Forgotpass(models.Model):
	user=models.ForeignKey(User)
	auth=models.CharField(max_length = 100)
	time=models.DateTimeField(null=True,blank=True)
	def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		z=timezone('Asia/Kolkata')
		fmt='%Y-%m-%d %H:%M:%S'
		ind_time=datetime.now(z)
		self.time = ind_time.strftime(fmt)
		super(Forgotpass, self).save(*args, **kwargs)


class X(models.Model):
	Name = models.CharField(max_length = 100)
	C=models.ImageField(upload_to = 'shipment/')
	order=models.ForeignKey(Order,null=True)

class LoginSession(models.Model):
	user=models.ForeignKey(User,null=True,blank=True)
	time=models.DateTimeField(null=True,blank=True)
	success=models.CharField(max_length=100,
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


class Weborder(models.Model):
	item_details=models.CharField(max_length = 100)
	pickup_location=models.CharField(max_length = 4000)
	pincode=models.CharField(max_length = 56)
	number=models.CharField(max_length = 51)
	time=models.DateTimeField(null=True,blank=True)


	def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		z=timezone('Asia/Kolkata')
		fmt='%Y-%m-%d %H:%M:%S'
		ind_time=datetime.now(z)
		self.time = ind_time.strftime(fmt)
		super(Weborder, self).save(*args, **kwargs)



class Priceapp(models.Model):
	weight=models.CharField(max_length = 10)
	pincode=models.CharField(max_length = 60)
	l=models.CharField(max_length = 10)
	b=models.CharField(max_length = 10)
	h=models.CharField(max_length = 10)
	

class Dateapp(models.Model):
	pincode=models.CharField(max_length = 60)














