# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20150412_1020'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shipment',
            old_name='tracking_no',
            new_name='real_tracking_no',
        ),
    ]
