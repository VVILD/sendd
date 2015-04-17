# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_order_book_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='cancelled',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default=b'F', max_length=1, choices=[(b'P', b'pending'), (b'C', b'complete'), (b'N', b'cancelled'), (b'F', b'fake')]),
            preserve_default=True,
        ),
    ]
