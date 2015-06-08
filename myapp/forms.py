from django.forms import ModelForm, Textarea
from django import forms
from myapp.models import Shipment,Order,User,Namemail,Address
from suit.widgets import AutosizedTextarea

class ShipmentForm(ModelForm):
	class Meta:
		model = Shipment
		widgets = {
			'tracking_data': Textarea(attrs={'cols': 80, 'rows': 20}),
		}


class OrderForm(ModelForm):


	item_details=forms.CharField(required=False)
	contact_number=forms.CharField(required=False)
	drop_name=forms.CharField(required=False)
	drop_phone=forms.CharField(required=False)
	flat_no=forms.CharField(initial='400076',required=False)
	drop_flat_no=forms.CharField(initial='400076',required=False)
	locality=forms.CharField(initial='400076',required=False)
	city=forms.CharField(initial='400076',required=False)
	state=forms.CharField(initial='400076',required=False)
	drop_pincode=forms.CharField(initial='400076',required=False)
	country=forms.CharField(initial='India',required=False)


	def save(self,commit=True):
		item_details = self.cleaned_data.get('item_details', None)
		name = self.cleaned_data.get('name', None)
		email = self.cleaned_data.get('email', None)
		number = self.cleaned_data.get('contact_number', None)
		drop_flat_no=self.cleaned_data.get('drop_flat_no', None)
		locality=self.cleaned_data.get('locality', None)
		city=self.cleaned_data.get('city', None)
		state=self.cleaned_data.get('state', None)
		drop_pincode=self.cleaned_data.get('drop_pincode', None)
		country=self.cleaned_data.get('country', None)
		drop_name=self.cleaned_data.get('drop_name', None)
		drop_phone=self.cleaned_data.get('drop_phone', None)
		try:
			user=User.objects.get(pk=number)
		except:
			user=User.objects.create(phone=number)

		namemail=Namemail.objects.filter(name=name,email=email,user=user)
		if (namemail.count()==0):
			namemail=Namemail.objects.create(name=name,email=email,user=user)
		else:
			for x in namemail:
				namemail=x

			
		


		# ...do something with extra_field here...
		#shipment=Shipment.objects.create(item_name=item_details)		
		#user=User.objects.get(pk=8879006197)
		#shipment=Order.objects.create(user=user)	
	# flat_no=models.CharField(max_length = 100,null=True,blank =True)
	# locality=models.CharField(max_length = 200,null=True,blank =True)
	# city=models.CharField(max_length = 50,null=True,blank =True)
	# state=models.CharField(max_length = 50,null=True,blank =True)
	# pincode=models.CharField(max_length =30,null=True,blank =True)
	# country=models.CharField(max_length =30,null=True,blank =True)

		print "shit"
		print self.cleaned_data["flat_no"]
		self.cleaned_data["flat_no"]='45555'
		print self.cleaned_data["flat_no"]
		print self.cleaned_data
		print commit
		instance = super(OrderForm, self).save(commit=False)
		instance.flat_no='dasdsa'
		instance.namemail=namemail
		instance.save()

		print instance.pk
		order=Order.objects.get(pk=instance.pk)
		address=Address.objects.create(flat_no=drop_flat_no,locality=locality,city=city,state=state,pincode=drop_pincode,country=country)
		shipment=Shipment.objects.create(item_name=item_details,order=order,drop_name=drop_name,drop_phone=drop_phone,drop_address=address)

		return instance



	class Meta:
		model= Order
		widgets = {
			'address': AutosizedTextarea,
			}

