# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('businessapp', '0002_auto_20150611_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='applied_weight',
            field=models.IntegerField(max_length=10, null=True, blank=True),
            preserve_default=True,
        ),
    ]
