# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_auto_20150412_1022'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shipment',
            old_name='trackno',
            new_name='tracking_no',
        ),
    ]
