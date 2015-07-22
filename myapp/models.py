from django.db.models.signals import post_save
from django.db import models
from django.core.validators import RegexValidator
import hashlib
from datetime import datetime,timedelta
from pytz import timezone
import pytz
import random
from push_notifications.models import APNSDevice, GCMDevice
from django.utils.encoding import force_bytes


class Pricing(models.Model):
	amount_charged_by_courier=models.IntegerField(null=True,blank=True)
	amount_spent_in_packingpickup=models.IntegerField(null=True,blank=True)
	amount_paid=models.IntegerField(null=True,blank=True)

	def __unicode__(self):
		return str(self.amount_paid-self.amount_charged_by_courier-self.amount_spent_in_packingpickup)

class User(models.Model):
	phone_regex = RegexValidator(regex=r'^[0-9]*$', message="Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")
	phone = models.CharField(validators=[phone_regex],max_length = 12,primary_key=True)
	name = models.CharField(max_length = 100,null=True,blank =True)
	password=models.CharField(max_length = 300,null=True,blank =True)
	email = models.EmailField(max_length = 75,null=True,blank =True)
	otp=models.IntegerField(null=True,blank=True)
	apikey= models.CharField(max_length = 100,null=True,blank=True)
	referral_code= models.CharField(max_length = 50,null=True,blank=True)
	time=models.DateTimeField(null=True,blank=True)
	gcmid=models.TextField(null=True,blank=True)
	deviceid= models.CharField(max_length = 25,null=True,blank=True)
	
	def save(self, *args, **kwargs):
		z=timezone('Asia/Kolkata')
		fmt='%Y-%m-%d %H:%M:%S'
		ind_time=datetime.now(z)
		self.time = ind_time.strftime(fmt)
		super(User, self).save(*args, **kwargs)


	def __unicode__(self):
		return str(self.phone)

class Address(models.Model):
	flat_no=models.CharField(max_length = 100,null=True,blank =True)
	locality=models.CharField(max_length = 200,null=True,blank =True)
	city=models.CharField(max_length = 50,null=True,blank =True)
	state=models.CharField(max_length = 50,null=True,blank =True)
	pincode=models.CharField(max_length =30,null=True,blank =True)
	country=models.CharField(max_length =30,null=True,blank =True)
	def __unicode__(self):
		return str(str(self.flat_no)+ ',' + str(self.locality)+ ',' + str(self.city) + ',' + str(self.state)+',' + str(self.country)+ ',' + str(self.pincode))

class Namemail(models.Model):
	nm_no=models.AutoField(primary_key=True)
	name=models.CharField(max_length = 160,null=True,blank =True)
	email = models.EmailField(max_length = 75,null=True,blank =True)
	user=models.ForeignKey(User)

class Promocode(models.Model):
	code=models.CharField(max_length = 20,primary_key=True)
	msg=models.CharField(max_length = 150)
	only_for_first=models.CharField(max_length=1,choices=(('Y','yes') ,('N','no'),),)
	def __unicode__(self):
		return str(self.code)


class Pickupboy(models.Model):
	name=models.CharField(max_length=40)
	phone=models.CharField(max_length=10,primary_key=True)

	def __unicode__(self):
		return str(self.name)

class Order(models.Model):
	order_no=models.AutoField(primary_key=True)
	date=models.DateField(verbose_name='pickup date',null=True,blank =True)
	time=models.TimeField(verbose_name='pickup time',null=True,blank =True)
	user=models.ForeignKey(User)
	promocode=models.ForeignKey(Promocode,null=True,blank=True)
	
	namemail=models.ForeignKey(Namemail,null=True,blank=True)
	name = models.CharField(max_length = 100,null=True,blank =True)
	email = models.EmailField(max_length = 75,null=True,blank =True)
	status=models.CharField(max_length=1,
									  choices=(('P','pending') ,('C','complete'),('N','cancelled'),('F','fake'),),
									  default='P')

	order_status=models.CharField(max_length=2,
									  choices=(('O','order_recieved') ,('A','Alloted'),('P','picked up'),('Pa','packed'),('C','completed'),('D','delivered'),('N','cancelled'),('F','fake'),('Q','query'),),null=True,blank=True,default='O')


	comment=models.TextField(null=True,blank=True)
	way=models.CharField(max_length=1,
									  choices=(('A','app') ,('W','web'),('C','call'),),
									  default='A')
	pick_now=models.CharField(max_length=1,
									  choices=(('Y','yes') ,('N','no'),),
									  default='Y')
	#source=models.CharField(max_length=1,
	#								  choices=(('P','pending') ,('C','complete'),('N','cancelled'),('F','fake'),),
	#								  default='F')
	#cost=models.CharField(max_length = 10,null=True ,blank=True)
	#paid=models.CharField(max_length=1,
	#								  choices=(('Y','yes') ,('N','no'),),
	#								  blank=True , null = True)

	#cancelled=models.CharField(max_length=1,
	#								  choices=(('Y','yes') ,('N','no'),),
	#								  default='N')
	pickupboy=models.ForeignKey(Pickupboy,null=True,blank=True)
	latitude = models.DecimalField(max_digits=25, decimal_places=20,null=True ,blank=True)
	longitude = models.DecimalField(max_digits=25, decimal_places=20,null=True ,blank=True)
	address=models.CharField(max_length = 200,null=True ,blank=True)	
	pincode=models.CharField(max_length =30,null=True ,blank=True)
	flat_no=models.CharField(max_length =100,null=True ,blank=True)
	#picked_up=models.BooleanField(default=False

	book_time=models.DateTimeField(null=True,blank=True)
	

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


class ReceivedOrder(Order):
	class Meta:
		proxy=True


class AllotedOrder(Order):
	class Meta:
		proxy=True
class PickedupOrder(Order):
	class Meta:
		proxy=True
class PackedOrder(Order):
	class Meta:
		proxy=True
class CompletedOrder(Order):
	class Meta:
		proxy=True
class FakeOrder(Order):
	class Meta:
		proxy=True


class QueryOrder(Order):
	class Meta:
		proxy=True		


class Shipment(models.Model):
	
	weight=models.CharField(verbose_name='item weight',max_length=10,null=True,blank=True)
	price=models.CharField(max_length=10,null=True,blank=True)
	
	name=models.CharField(verbose_name='item name',max_length=50,null=True,blank=True)
	
	tracking_no=models.AutoField(primary_key=True)
	real_tracking_no=models.CharField(max_length=10,blank=True,null=True)
	mapped_tracking_no=models.CharField(max_length = 50,null=True,blank=True)
	tracking_data=models.CharField(max_length = 8000,null=True,blank=True)
	img=models.ImageField(upload_to = 'shipment/',null=True,blank=True)	
	category=models.CharField(max_length=1,
									  choices=(('P','premium') ,('S','standard'),('E','economy'),),
									  default='P',blank=True , null = True)
	drop_name=models.CharField(max_length = 100,null=True,blank=True)
	
	phone_regex2 = RegexValidator(regex=r'^[0-9]{10,11}$', message="Phone number must be entered in the format: '999999999'. And be of 10 digits.")

	drop_phone = models.CharField(validators=[phone_regex2],max_length =16,null=True,blank=True)
	drop_address=models.ForeignKey(Address,null=True,blank=True)
	order=models.ForeignKey(Order,null=True,blank=True)
	



	status=models.CharField(max_length=1,
									  choices=(('P','pending') ,('C','complete'),),
									  default='P',null=True,blank=True)
	
	paid=models.CharField(max_length=10,
									  choices=(('Paid','Paid') ,('Not Paid','Not Paid'),),
									  blank=True , null = True ,default='Not Paid')
	company=models.CharField(max_length=1,
									  choices=(('F','FedEx') ,('D','Delhivery'),),
									  blank=True , null = True)

	company=models.CharField(max_length=2,
									  choices=[('F','FedEx') ,('D','Delhivery'),('P','Professional'),('G','Gati'),('A','Aramex'),('E','Ecomexpress'),('DT','dtdc'),('FF','First Flight'),('M','Maruti courier')],
									  blank=True , null = True)

	pricing=models.ForeignKey(Pricing,null=True,blank=True)
	cost_of_courier= models.CharField(verbose_name='item cost',max_length = 100,null=True,blank=True)
	item_name=models.CharField(max_length = 100,null=True,blank=True)
	kartrocket_order=models.CharField(max_length = 100,null=True,blank=True)


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
			p = Pricing.objects.create(amount_charged_by_courier=0, amount_spent_in_packingpickup=0,amount_paid=0)
			self.pricing=p
			kwargs['force_update'] = True
			kwargs['force_insert'] = False
			
			print "H"
		super(Shipment, self).save(*args, **kwargs)
		print "L"

	


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



class Gcmmessage(models.Model):
	title=models.CharField(max_length = 60)
	message=models.TextField()
	def __unicode__(self):
		return str(self.message)


	def save(self, *args, **kwargs):
		''' On save, update timestamps '''
		try:
			devices=GCMDevice.objects.all()
			devices.send_message(self.message,extra={"title":self.title})
			#device = GCMDevice.objects.get(registration_id='APA91bEjN-CdfjLJd4PGJRu4z3k0pbY8wndZddW2tIc5mcsU_b6UhjgbOLDniWYYd_9GZ4MPPAwh0Wva-_dPsl-fabuteKKV262VljMCt3msxhmoCBcGrq675OLw8zIQYzxopHqfeGgQ')
			#device.send_message("harsh bahut bada chakka hai.harsh", extra={"tracking_no": "S134807P31","url":"http://128.199.159.90/static/IMG_20150508_144433.jpeg"})
		except:
			pass
		super(Gcmmessage, self).save(*args, **kwargs)

class Promocheck(models.Model):
	code=models.CharField(max_length = 20)
	user=models.ForeignKey(User,null=True,blank=True)
	valid=models.CharField(max_length=1,choices=(('Y','yes') ,('N','no'),),)


	

class Pincodecheck(models.Model):
	pincode=models.CharField(max_length=6)
	def __unicode__(self):
		return str(self.pincode)


	def send_update(sender, instance, created, **kwargs):
		print "shittt>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
		print instance.pk
		#quersyset.filter(pk=instance.pk).update(....)
		#MyModel.objects.filter(pk=some_value).update(field1='some value')


	post_save.connect(send_update, sender=Shipment)



class Zipcode(models.Model):
	pincode=models.CharField(max_length=6,primary_key=True)
	zone=models.CharField(max_length=1)
	city=models.CharField(max_length=56)
	state=models.CharField(max_length=56)
	cod=models.BooleanField(default=False)
	fedex=models.BooleanField(default=False)
	aramex=models.BooleanField(default=False)
	delhivery=models.BooleanField(default=False)
	ecom=models.BooleanField(default=False)
	firstflight=models.BooleanField(default=False)
	def __unicode__(self):
		return str(self.pincode)



class Invoicesent(models.Model):
	order=models.ForeignKey(Order)





