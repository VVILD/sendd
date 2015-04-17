# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_auto_20150416_2252'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='book_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
