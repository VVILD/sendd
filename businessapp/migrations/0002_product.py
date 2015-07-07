# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('businessapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('quantity', models.IntegerField(max_length=10, null=True, blank=True)),
                ('sku', models.CharField(max_length=100, null=True, blank=True)),
                ('price', models.IntegerField(max_length=10, null=True, blank=True)),
                ('weight', models.FloatField(max_length=10, null=True, blank=True)),
                ('applied_weight', models.FloatField(max_length=10, null=True, blank=True)),
                ('real_tracking_no', models.CharField(max_length=10, null=True, blank=True)),
                ('mapped_tracking_no', models.CharField(max_length=50, null=True, blank=True)),
                ('tracking_data', models.CharField(max_length=8000, null=True, blank=True)),
                ('kartrocket_order', models.CharField(max_length=100, null=True, blank=True)),
                ('company', models.CharField(blank=True, max_length=1, null=True, choices=[(b'F', b'FedEx'), (b'D', b'Delhivery')])),
                ('shipping_cost', models.IntegerField(null=True, blank=True)),
                ('cod_cost', models.IntegerField(default=0, null=True, blank=True)),
                ('status', models.CharField(default=b'P', max_length=1, null=True, blank=True, choices=[(b'P', b'pending'), (b'C', b'complete')])),
                ('date', models.DateTimeField(null=True, blank=True)),
                ('order', models.ForeignKey(blank=True, to='businessapp.Order', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
