from django.db import models


class StateCodes(models.Model):
    country_code = models.CharField(max_length=2)
    subdivision_name = models.CharField(max_length=128)
    code = models.CharField(max_length=10)


class Pincode(models.Model):
    """
    Model for pincodes. Synced with OGD database
    """
    id = models.PositiveIntegerField(
        verbose_name='id',
        primary_key=True,
        unique=True
    )
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

    def __str__(self):
        return "{0} : {1}".format(self.pincode, self.office_name)

    class Meta:
        verbose_name = 'ogd pincodes'
        ordering = ['id', 'pincode']