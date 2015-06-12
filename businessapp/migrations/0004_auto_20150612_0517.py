# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('businessapp', '0003_product_applied_weight'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='refrence_id',
            new_name='reference_id',
        ),
    ]
