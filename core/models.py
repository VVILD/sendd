from django.db import models


class StateCodes(models.Model):
    country_code = models.CharField(max_length=2)
    subdivision_name = models.CharField(max_length=128)
    code = models.CharField(max_length=10)
