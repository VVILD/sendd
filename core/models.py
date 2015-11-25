from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save

from core.tasks import new_warehouse_reassignment
from core.utils import state_matcher


class Warehouse(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(
        verbose_name='created at',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='updated at',
        auto_now=True
    )
    name = models.CharField(
        verbose_name='warehouse name',
        max_length=255
    )
    address_line_1 = models.CharField(
        verbose_name='address line 1',
        max_length=70
    )
    address_line_2 = models.CharField(
        verbose_name='address line 2',
        max_length=70,
        blank=True,
        null=True
    )
    city = models.CharField(
        verbose_name='city',
        max_length=50
    )
    state = models.CharField(
        verbose_name='state',
        max_length=50
    )
    pincode = models.CharField(
        verbose_name='pincode',
        max_length=20
    )
    lat = models.FloatField(blank=True, null=True)
    long = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.state:
            if not state_matcher.is_state(self.state):
                closest_state = state_matcher.get_closest_state(self.state)
                if closest_state:
                    self.state = closest_state[0]
        else:
            raise ValidationError("Please enter a valid state")

        super(Warehouse, self).save(*args, **kwargs)


def warehouse_reassign(sender, instance, created, **kwargs):
    if instance.pincode and created:
        new_warehouse_reassignment.delay(instance.pk)


post_save.connect(warehouse_reassign, sender=Warehouse)


class StateCodes(models.Model):
    country_code = models.CharField(max_length=2)
    subdivision_name = models.CharField(max_length=128)
    code = models.CharField(max_length=10)


class Pincode(models.Model):
    """
    Model for pincodes. Synced with OGD database
    """
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(
        verbose_name='created at',
        auto_now_add=True
    )
    office_name = models.CharField(
        verbose_name='office name',
        max_length=100,
        null=True,
        blank=True
    )
    pincode = models.CharField(
        verbose_name='pincode',
        max_length=50,
    )
    office_type = models.CharField(
        verbose_name='office type',
        max_length=100,
        null=True,
        blank=True
    )
    division_name = models.CharField(
        verbose_name='division name',
        max_length=50,
        null=True,
        blank=True
    )
    region_name = models.CharField(
        verbose_name='region name',
        max_length=50,
        null=True,
        blank=True
    )
    circle_name = models.CharField(
        verbose_name='circle name',
        max_length=50,
        null=True,
        blank=True
    )
    taluk = models.CharField(
        verbose_name='taluk name',
        max_length=100,
        null=True,
        blank=True
    )
    district_name = models.CharField(
        verbose_name='district name',
        max_length=100,
        null=True,
        blank=True
    )
    state_name = models.CharField(
        verbose_name='state name',
        max_length=100,
        null=True,
        blank=True
    )
    telephone = models.CharField(
        verbose_name='phone number',
        max_length=50,
        null=True,
        blank=True
    )
    related_suboffice = models.CharField(
        verbose_name='related suboffice',
        max_length=200,
        null=True,
        blank=True
    )
    related_headoffice = models.CharField(
        verbose_name='related headoffice',
        max_length=100,
        null=True,
        blank=True
    )
    latitude = models.FloatField(
        blank=True,
        null=True
    )
    longitude = models.FloatField(
        blank=True,
        null=True
    )
    fedex_oda_opa = models.BooleanField(default=False)
    fedex_cod_service = models.BooleanField(default=False)
    fedex_servicable = models.BooleanField(default=False)
    ecom_servicable = models.BooleanField(default=False)
    warehouse = models.ForeignKey(Warehouse, null=True, blank=True, related_name="pincode_warehouse")

    def __str__(self):
        return "{0} : {1}".format(self.pincode, self.office_name)

    class Meta:
        verbose_name = 'ogd pincodes'
        ordering = ['id', 'pincode']


class Offline(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    message = models.TextField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.message


class EcomAWB(models.Model):
    awb = models.CharField(max_length=10, unique=True)
    label_type = models.CharField(max_length=1, choices=(('P', 'Prepaid'), ('C', 'COD')))
    used = models.BooleanField(default=False)

    def is_used(self):
        return self.used
