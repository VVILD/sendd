from django.forms import ModelForm, Textarea, HiddenInput
from django import forms
from myapp.mail.bookingConfirmationMail import SendConfirmationMail
from myapp.models import Shipment, Order, User, Namemail, Address
from suit.widgets import AutosizedTextarea
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from businessapp.models import Product,AddressDetails
import json
from django.contrib.admin import widgets

class NewQcCommentForm(ModelForm):
	new_comment=forms.CharField(max_length=100,required=False)
	class Meta:
		model = Product
		widgets = {
			'new_comment': Textarea(attrs={'cols': 80, 'rows': 20}),
		}


	def clean(self):
		
		new_comment=self.cleaned_data['new_comment']
		self.cleaned_data['qc_comment']= self.cleaned_data['qc_comment'] + '<br><br> ' + str(new_comment)


class NewReturnForm(ModelForm):
	class Meta:
		model = Product
		fields = ['status', 'return_action']

        def clean(self):
            if self.cleaned_data['return_action']:
                if self.cleaned_data['status']!='R':
                    raise forms.ValidationError("You cannot add a return_action unless status is return")



class NewTrackingStatus(ModelForm):
	tstatus=forms.CharField(max_length=100,required=False)
	location=forms.CharField(max_length=100,required=False)
	ttime=forms.DateTimeField()
	class Meta:
		model = Product

	def __init__(self, *args, **kwargs):
		super(NewTrackingStatus, self).__init__(*args, **kwargs)
		self.fields['ttime'].widget = widgets.AdminSplitDateTime()

	def clean(self):
		tstatus=self.cleaned_data['tstatus']
		location=self.cleaned_data['location']
		ttime=self.cleaned_data['ttime']


		tracking_data=self.cleaned_data['tracking_data']
		tracking_list=list(json.loads(tracking_data))
		tracking_list.append({"status": tstatus , "date": str(ttime.strftime("%Y-%m-%d %H:%M:%S")), "location": location })
		self.cleaned_data['tracking_data']= json.dumps(tracking_list)


class AddressForm(ModelForm):
	class Meta:
		model = AddressDetails

class Approveconfirmform(ModelForm):
	sure=forms.BooleanField(initial=True)
	class Meta:
		model = Product
		fields = ('sure','status')
		widgets = {
			'status': HiddenInput,
		}

	def clean(self):
		if self.cleaned_data['sure']:
			self.cleaned_data['status']='Y'
			self.cleaned_data['is_approved']=True
		# else:
		# 	pass


class Completeconfirmform(ModelForm):
	sure=forms.BooleanField(initial=True)
	class Meta:
		model = Product
		fields = ('sure','status')
		widgets = {
			'status': HiddenInput,
		}

	def clean(self):
		if self.cleaned_data['sure']:
			self.cleaned_data['status']='C'

