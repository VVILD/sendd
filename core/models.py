from django.core.exceptions import ValidationError
from django.db import models
from geopy.distance import vincenty
from geopy.geocoders import googlev3
# from businessapp.models import Business
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
        if self.pincode:
            geolocator = googlev3.GoogleV3(api_key="AIzaSyBEfEgATQeVkoKUnaB4O9rIdX2K2Bsh63o")
            location = geolocator.geocode("{}, India".format(self.pincode))
            self.lat, self.long = location.latitude, location.longitude
            super(Warehouse, self).save(*args, **kwargs)

            pincodes = Pincode.objects.filter(region_name=self.city).exclude(latitude__isnull=True)
            warehouses = Warehouse.objects.filter(city=self.city)
            from businessapp.models import Business
            businesses = Business.objects.filter(pincode__isnull=False).exclude(pincode=u'')

            for pincode in pincodes:
                closest_warehouse = None
                min_dist = 9999.9999
                for warehouse in warehouses:
                    distance = vincenty((pincode.latitude, pincode.longitude), (warehouse.lat, warehouse.long)).kilometers
                    if distance < min_dist:
                        min_dist = distance
                        closest_warehouse = warehouse
                pincode.warehouse = closest_warehouse
                pincode.save()

            for business in businesses:
                pincode_search = Pincode.objects.filter(pincode=str(business.pincode)).exclude(latitude__isnull=True, warehouse__isnull=True)
                if pincode_search.count() > 0:
                    business.warehouse = pincode_search[0].warehouse
                else:
                    business.warehouse = None
                business.save()
        else:
            raise ValidationError("Please enter a pincode")
        if self.state:
            if not state_matcher.is_state(self.state):
                closest_state = state_matcher.get_closest_state(self.state)
                if closest_state:
                    self.state = closest_state[0]
        else:
            raise ValidationError("Please enter a state")
        super(Warehouse, self).save(*args, **kwargs)


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