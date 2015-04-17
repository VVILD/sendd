# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='real_tracking_no',
            field=models.CharField(max_length=10, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shipment',
            name='tracking_no',
            field=models.AutoField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
