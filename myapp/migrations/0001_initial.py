# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flat_no', models.CharField(max_length=100)),
                ('locality', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('pincode', models.CharField(max_length=30)),
                ('country', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dateapp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pincode', models.CharField(max_length=60)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Forgotpass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('auth', models.CharField(max_length=100)),
                ('time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LoginSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(null=True, blank=True)),
                ('success', models.CharField(default=b'wrongpassword', max_length=100, choices=[(b'notregistered', b'notregistered'), (b'wrongpassword', b'wrongpassword'), (b'success', b'success')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_no', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.DateField(null=True, blank=True)),
                ('time', models.TimeField(null=True, blank=True)),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'P', b'pending'), (b'C', b'complete')])),
                ('cost', models.CharField(max_length=10, null=True, blank=True)),
                ('paid', models.CharField(blank=True, max_length=1, null=True, choices=[(b'Y', b'yes'), (b'N', b'no')])),
                ('cancelled', models.CharField(default=b'N', max_length=1, choices=[(b'Y', b'yes'), (b'N', b'no')])),
                ('latitude', models.DecimalField(null=True, max_digits=25, decimal_places=20, blank=True)),
                ('longitude', models.DecimalField(null=True, max_digits=25, decimal_places=20, blank=True)),
                ('address', models.CharField(max_length=200, null=True, blank=True)),
                ('pincode', models.CharField(max_length=30, null=True, blank=True)),
                ('flat_no', models.CharField(max_length=100, null=True, blank=True)),
                ('picked_up', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Priceapp',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.CharField(max_length=10)),
                ('pincode', models.CharField(max_length=60)),
                ('l', models.CharField(max_length=10)),
                ('b', models.CharField(max_length=10)),
                ('h', models.CharField(max_length=10)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('weight', models.CharField(max_length=10, null=True, blank=True)),
                ('price', models.CharField(max_length=10, null=True, blank=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
                ('tracking_no', models.IntegerField()),
                ('real_tracking_no', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('mapped_tracking_no', models.CharField(max_length=50, null=True, blank=True)),
                ('tracking_data', models.CharField(max_length=8000, null=True, blank=True)),
                ('img', models.ImageField(upload_to=b'shipment/')),
                ('category', models.CharField(blank=True, max_length=1, null=True, choices=[(b'P', b'premium'), (b'S', b'standard'), (b'E', b'economy')])),
                ('drop_name', models.CharField(max_length=100, null=True)),
                ('drop_phone', models.CharField(max_length=12, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[0-9]*$', message=b"Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'P', b'pending'), (b'C', b'complete')])),
                ('paid', models.CharField(default=b'Not Paid', max_length=10, null=True, blank=True, choices=[(b'Paid', b'Paid'), (b'Not Paid', b'Not Paid')])),
                ('company', models.CharField(blank=True, max_length=1, null=True, choices=[(b'F', b'FedEx'), (b'D', b'Delhivery')])),
                ('drop_address', models.ForeignKey(to='myapp.Address', null=True)),
                ('order', models.ForeignKey(to='myapp.Order', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('phone', models.CharField(max_length=12, serialize=False, primary_key=True, validators=[django.core.validators.RegexValidator(regex=b'^[0-9]*$', message=b"Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")])),
                ('name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=300)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('otp', models.IntegerField(null=True, blank=True)),
                ('apikey', models.CharField(max_length=100, null=True, blank=True)),
                ('referral_code', models.CharField(max_length=50, null=True, blank=True)),
                ('time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Weborder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_details', models.CharField(max_length=100)),
                ('pickup_location', models.CharField(max_length=4000)),
                ('pincode', models.CharField(max_length=56)),
                ('number', models.CharField(max_length=51)),
                ('time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='X',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('Name', models.CharField(max_length=100)),
                ('C', models.ImageField(upload_to=b'shipment/')),
                ('order', models.ForeignKey(to='myapp.Order', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(to='myapp.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='loginsession',
            name='user',
            field=models.ForeignKey(blank=True, to='myapp.User', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='forgotpass',
            name='user',
            field=models.ForeignKey(to='myapp.User'),
            preserve_default=True,
        ),
    ]
