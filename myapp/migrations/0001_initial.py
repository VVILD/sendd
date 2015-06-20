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
                ('flat_no', models.CharField(max_length=100, null=True, blank=True)),
                ('locality', models.CharField(max_length=200, null=True, blank=True)),
                ('city', models.CharField(max_length=50, null=True, blank=True)),
                ('state', models.CharField(max_length=50, null=True, blank=True)),
                ('pincode', models.CharField(max_length=30, null=True, blank=True)),
                ('country', models.CharField(max_length=30, null=True, blank=True)),
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
            name='Gcmmessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60)),
                ('message', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invoicesent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
            name='Namemail',
            fields=[
                ('nm_no', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=160, null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_no', models.AutoField(serialize=False, primary_key=True)),
                ('date', models.DateField(null=True, verbose_name=b'pickup date', blank=True)),
                ('time', models.TimeField(null=True, verbose_name=b'pickup time', blank=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'P', b'pending'), (b'C', b'complete'), (b'N', b'cancelled'), (b'F', b'fake')])),
                ('way', models.CharField(default=b'A', max_length=1, choices=[(b'A', b'app'), (b'W', b'web'), (b'C', b'call')])),
                ('pick_now', models.CharField(default=b'Y', max_length=1, choices=[(b'Y', b'yes'), (b'N', b'no')])),
                ('latitude', models.DecimalField(null=True, max_digits=25, decimal_places=20, blank=True)),
                ('longitude', models.DecimalField(null=True, max_digits=25, decimal_places=20, blank=True)),
                ('address', models.CharField(max_length=200, null=True, blank=True)),
                ('pincode', models.CharField(max_length=30, null=True, blank=True)),
                ('flat_no', models.CharField(max_length=100, null=True, blank=True)),
                ('book_time', models.DateTimeField(null=True, blank=True)),
                ('namemail', models.ForeignKey(blank=True, to='myapp.Namemail', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pincodecheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pincode', models.CharField(max_length=6)),
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
            name='Pricing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount_charged_by_courier', models.IntegerField(null=True, blank=True)),
                ('amount_spent_in_packingpickup', models.IntegerField(null=True, blank=True)),
                ('amount_paid', models.IntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Promocheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=20)),
                ('valid', models.CharField(max_length=1, choices=[(b'Y', b'yes'), (b'N', b'no')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Promocode',
            fields=[
                ('code', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('msg', models.CharField(max_length=150)),
                ('only_for_first', models.CharField(max_length=1, choices=[(b'Y', b'yes'), (b'N', b'no')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Shipment',
            fields=[
                ('weight', models.CharField(max_length=10, null=True, verbose_name=b'item weight', blank=True)),
                ('price', models.CharField(max_length=10, null=True, blank=True)),
                ('name', models.CharField(max_length=50, null=True, verbose_name=b'item name', blank=True)),
                ('tracking_no', models.AutoField(serialize=False, primary_key=True)),
                ('real_tracking_no', models.CharField(max_length=10, null=True, blank=True)),
                ('mapped_tracking_no', models.CharField(max_length=50, null=True, blank=True)),
                ('tracking_data', models.CharField(max_length=8000, null=True, blank=True)),
                ('img', models.ImageField(null=True, upload_to=b'shipment/', blank=True)),
                ('category', models.CharField(default=b'P', max_length=1, null=True, blank=True, choices=[(b'P', b'premium'), (b'S', b'standard'), (b'E', b'economy')])),
                ('drop_name', models.CharField(max_length=100, null=True, blank=True)),
                ('drop_phone', models.CharField(max_length=16, null=True, blank=True)),
                ('status', models.CharField(default=b'P', max_length=1, null=True, blank=True, choices=[(b'P', b'pending'), (b'C', b'complete')])),
                ('paid', models.CharField(default=b'Not Paid', max_length=10, null=True, blank=True, choices=[(b'Paid', b'Paid'), (b'Not Paid', b'Not Paid')])),
                ('company', models.CharField(blank=True, max_length=1, null=True, choices=[(b'F', b'FedEx'), (b'D', b'Delhivery')])),
                ('cost_of_courier', models.CharField(max_length=100, null=True, verbose_name=b'item cost', blank=True)),
                ('item_name', models.CharField(max_length=100, null=True, blank=True)),
                ('drop_address', models.ForeignKey(blank=True, to='myapp.Address', null=True)),
                ('order', models.ForeignKey(blank=True, to='myapp.Order', null=True)),
                ('pricing', models.ForeignKey(blank=True, to='myapp.Pricing', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('phone', models.CharField(max_length=12, serialize=False, primary_key=True, validators=[django.core.validators.RegexValidator(regex=b'^[0-9]*$', message=b"Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")])),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('password', models.CharField(max_length=300, null=True, blank=True)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('otp', models.IntegerField(null=True, blank=True)),
                ('apikey', models.CharField(max_length=100, null=True, blank=True)),
                ('referral_code', models.CharField(max_length=50, null=True, blank=True)),
                ('time', models.DateTimeField(null=True, blank=True)),
                ('gcmid', models.TextField(null=True, blank=True)),
                ('deviceid', models.CharField(max_length=25, null=True, blank=True)),
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
            model_name='promocheck',
            name='user',
            field=models.ForeignKey(blank=True, to='myapp.User', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='promocode',
            field=models.ForeignKey(blank=True, to='myapp.Promocode', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(to='myapp.User'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='namemail',
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
            model_name='invoicesent',
            name='order',
            field=models.ForeignKey(to='myapp.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='forgotpass',
            name='user',
            field=models.ForeignKey(to='myapp.User'),
            preserve_default=True,
        ),
    ]
