from django.core.validators import RegexValidator
from django.db import models

__author__ = 'vatsalshah'


class PBPincodes(models.Model):
    pincode = models.CharField(max_length=30, null=True, blank=True)

    def __unicode__(self):
        return str(self.pincode)


class PBUser(models.Model):
    phone_regex = RegexValidator(regex=r'^[0-9]*$',
                                 message="Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=10, primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    otp = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.CharField(null=True, blank=True, max_length=255)
    doc_url = models.CharField(null=True, blank=True, max_length=255)
    pincodes = models.ManyToManyField(PBPincodes)
    status = models.CharField(max_length=1,
                              choices=(('A', 'Active'), ('T', 'Terminated'), ('V', 'Vacation'), ('S', 'Sabbatical')),
                              default='A')

    def __unicode__(self):
        return str(self.name)


class PBLocations(models.Model):
    pbuser = models.ForeignKey(PBUser)
    updated_at = models.DateTimeField(auto_now=True)
    lon = models.FloatField()
    lat = models.FloatField()
