from django.forms import ModelForm, Textarea
from django import forms
from myapp.mail.bookingConfirmationMail import SendConfirmationMail
from myapp.models import Shipment, Order, User, Namemail, Address
from suit.widgets import AutosizedTextarea
from django.core.mail import send_mail
from django.core.validators import RegexValidator


class ShipmentForm(ModelForm):
    class Meta:
        model = Shipment
        widgets = {
            'tracking_data': Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class OrderEditForm(ModelForm):
    class Meta:
        model = Order

class NewShipmentForm(ModelForm):
    #xx=forms.CharField(max_length=50)
    class Meta():
        model = Shipment
    #    fields =  ['xx']
#           exclude=['last_tracking_status','qc_comment','tracking_history']


class NewShipmentAddForm(ModelForm):
    addressline1=forms.CharField(max_length=200,required=False)
    addressline2=forms.CharField(max_length=200,required=False)
    pincode=forms.CharField(max_length=50,required=False)
    city=forms.CharField(max_length=50,required=False)
    state=forms.CharField(max_length=50,required=False)
    country=forms.CharField(max_length=50,required=False)
    print "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
    class Meta:
        model = Shipment


    def clean(self):
        
        addressline1=self.cleaned_data['addressline1']
        addressline2=self.cleaned_data['addressline2']
        pincode=self.cleaned_data['pincode']
        city=self.cleaned_data['city']
        state=self.cleaned_data['state']
        country=self.cleaned_data['country']

                
        address = Address.objects.create(flat_no=addressline1, locality=addressline2, city=city, state=state,
                                         pincode=pincode, country=country)

        pk=address.pk

        self.cleaned_data['drop_address']=Address.objects.get(pk=pk)

    # def save(self, commit=True):
    #     address = Address.objects.create(flat_no=addressline1, locality=addressline2, city=city, state=state,
    #                                       pincode=pincode, country=country)
    #     shipment = Shipment(item_name=item_details, order=order, drop_name=drop_name,
    #                                        drop_phone=drop_phone, drop_address=address)
    #     shipment.save()


# class RegisterEmailForm(RegisterBaseForm):
# first_name = forms.CharField(max_length=User._meta.get_field('first_name').max_length)
# last_name = forms.CharField(max_length=User._meta.get_field('last_name').max_length)
# class Meta(RegisterBaseForm.Meta):
# fields = RegisterBaseForm.Meta.fields + ('first_name', 'last_name')

class OrderForm(ModelForm):
    phone_regex2 = RegexValidator(regex=r'^[0-9]{10,11}$',
                                  message="Phone number must be entered in the format: '999999999'. And be of 10 digits.")

    item_details = forms.CharField()
    contact_number = forms.CharField(validators=[phone_regex2])
    name = forms.CharField()
    email = forms.CharField()
    drop_name = forms.CharField(required=False)
    drop_phone = forms.CharField(required=False)
    flat_no = forms.CharField(required=False)
    drop_flat_no = forms.CharField(required=False)
    locality = forms.CharField(required=False)
    city = forms.CharField(required=False)
    state = forms.CharField(required=False)
    drop_pincode = forms.CharField(required=False)
    country = forms.CharField(initial='India', required=False)
    # way=forms.CharField(initial='C',widget=forms.HiddenInput())

    def save(self, commit=True):
        item_details = self.cleaned_data.get('item_details', None)
        name = self.cleaned_data.get('name', None)
        email = self.cleaned_data.get('email', None)
        number = self.cleaned_data.get('contact_number', None)
        drop_flat_no = self.cleaned_data.get('drop_flat_no', None)
        locality = self.cleaned_data.get('locality', None)
        city = self.cleaned_data.get('city', None)
        state = self.cleaned_data.get('state', None)
        drop_pincode = self.cleaned_data.get('drop_pincode', None)
        country = self.cleaned_data.get('country', None)
        drop_name = self.cleaned_data.get('drop_name', None)
        drop_phone = self.cleaned_data.get('drop_phone', None)

        try:
            user = User.objects.get(pk=number)
        except:
            user = User.objects.create(phone=number)

        namemail = Namemail.objects.filter(name=name, email=email, user=user)
        if (namemail.count() == 0):
            namemail = Namemail.objects.create(name=name, email=email, user=user)
        else:
            for x in namemail:
                namemail = x





                # ...do something with extra_field here...
                # shipment=Shipment.objects.create(item_name=item_details)
                #user=User.objects.get(pk=8879006197)
                #shipment=Order.objects.create(user=user)
                # flat_no=models.CharField(max_length = 100,null=True,blank =True)
                # locality=models.CharField(max_length = 200,null=True,blank =True)
                # city=models.CharField(max_length = 50,null=True,blank =True)
                # state=models.CharField(max_length = 50,null=True,blank =True)
                # pincode=models.CharField(max_length =30,null=True,blank =True)
                # country=models.CharField(max_length =30,null=True,blank =True)

        print "shit"
        print commit
        instance = super(OrderForm, self).save(commit=False)
        instance.namemail = namemail
        instance.user = user
        instance.way = 'C'
        instance.order_status = 'O'
        instance.save()

        print instance.pk
        order = Order.objects.get(pk=instance.pk)
        address = Address.objects.create(flat_no=drop_flat_no, locality=locality, city=city, state=state,
                                         pincode=drop_pincode, country=country)
        shipment = Shipment.objects.create(item_name=item_details, order=order, drop_name=drop_name,
                                           drop_phone=drop_phone, drop_address=address)

        receiver = str(order.namemail.email)
        trackingID = str(shipment.real_tracking_no)
        senderName = str(order.namemail.name)
        senderContact = str(order.user.phone)
        pickupAddress = str(order.address)
        bookingTime = str(order.book_time.strftime("%H:%M:%S"))
        pickupTime = None
        if order.time:
            pickupTime = str(order.time)
        itemName = None
        if shipment.item_name is not None:
            itemName = str(shipment.item_name)
        itemImageURL = None
        if shipment.img.name is not None:
            print(str(shipment.img.name).split('/'))
            itemImageURL = str("http://sendmates.com/static/" + str(shipment.img.name))
        recipientName = None
        if shipment.drop_name is not None:
            recipientName = str(shipment.drop_name)
        recipientContact = None
        if shipment.drop_phone is not None:
            recipientContact = str(shipment.drop_phone)
        recipientAddress = None
        if shipment.drop_address is not None:
            recipientAddress = str(address)
        mailer = SendConfirmationMail(receiver=receiver, trackingID=trackingID, senderName=senderName,
                                      senderContact=senderContact, pickupAddress=pickupAddress,
                                      bookingTime=bookingTime, pickupTime=pickupTime, itemName=itemName,
                                      recipientName=recipientName, itemImageURL=itemImageURL,
                                      recipientContact=recipientContact, recipientAddress=recipientAddress)
        mailer.send()

        return instance


    class Meta:
        model = Order
        widgets = {
            'address': AutosizedTextarea,
            'locality': Textarea(attrs={'cols': 80, 'rows': 20}),
            'drop_flat_no': Textarea(attrs={'cols': 80, 'rows': 20}),
        }

