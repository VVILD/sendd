# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_auto_20150416_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='way',
            field=models.CharField(default=b'A', max_length=1, choices=[(b'A', b'app'), (b'W', b'web'), (b'C', b'call')]),
            preserve_default=True,
        ),
    ]
