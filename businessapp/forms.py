from django.forms import ModelForm, Textarea 
from django import forms
from myapp.mail.bookingConfirmationMail import SendConfirmationMail
from myapp.models import Shipment, Order, User, Namemail, Address
from suit.widgets import AutosizedTextarea
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from businessapp.models import Product
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

	STATUS_CHOICES = (
    ('in transit', ("in transit")),
    ('out for delivery', ("out for delivery")),
    ('Delivered', ("Delivered")),
    ('return in transit', ("return in transit")),
    ('Return', ("Return"))

)
	nstatus=forms.ChoiceField(choices = STATUS_CHOICES, label="", initial='', widget=forms.Select(), required=True)
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
		nstatus=self.cleaned_data['nstatus']
		location=self.cleaned_data['location']
		ttime=self.cleaned_data['ttime']


		tracking_data=self.cleaned_data['tracking_data']
		tracking_list=list(json.loads(tracking_data))
		tracking_list.append({"status": nstatus , "date": str(ttime.strftime("%Y-%m-%d %H:%M:%S")), "location": location })
		self.cleaned_data['tracking_data']= json.dumps(tracking_list)
		if nstatus == 'Delivered':
			self.cleaned_data['status']= 'C'
		if nstatus == 'Return' or nstatus == 'return in transit':
			self.cleaned_data['status']= 'R'


