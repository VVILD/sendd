# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_auto_20150416_2225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='cost',
        ),
        migrations.RemoveField(
            model_name='order',
            name='paid',
        ),
        migrations.RemoveField(
            model_name='order',
            name='picked_up',
        ),
    ]
