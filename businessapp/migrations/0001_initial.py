# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('username', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('business_name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=300)),
                ('email', models.EmailField(max_length=75)),
                ('name', models.CharField(max_length=100)),
                ('contact_mob', models.CharField(max_length=15)),
                ('contact_office', models.CharField(max_length=15, null=True, blank=True)),
                ('pickup_time', models.CharField(blank=True, max_length=1, null=True, choices=[(b'M', b'morning'), (b'N', b'noon'), (b'E', b'evening')])),
                ('address', models.CharField(max_length=315, null=True, blank=True)),
                ('city', models.CharField(max_length=50, null=True, blank=True)),
                ('state', models.CharField(max_length=50, null=True, blank=True)),
                ('pincode', models.CharField(max_length=50, null=True, blank=True)),
                ('company_name', models.CharField(max_length=100, null=True, blank=True)),
                ('website', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BusinessManager',
            fields=[
                ('user_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('phone', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='LoginSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(null=True, blank=True)),
                ('msg', models.CharField(default=b'wrongpassword', max_length=100, choices=[(b'notregistered', b'notregistered'), (b'wrongpassword', b'wrongpassword'), (b'success', b'success')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_no', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('phone', models.CharField(max_length=12)),
                ('street_address', models.CharField(max_length=300, null=True, blank=True)),
                ('city', models.CharField(max_length=50, null=True, blank=True)),
                ('state', models.CharField(max_length=50, null=True, blank=True)),
                ('pincode', models.CharField(max_length=30, null=True, blank=True)),
                ('country', models.CharField(max_length=30, null=True, blank=True)),
                ('payment_method', models.CharField(max_length=1, choices=[(b'F', b'free checkout'), (b'C', b'cod')])),
                ('book_time', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'P', b'pending'), (b'C', b'complete'), (b'N', b'cancelled'), (b'D', b'delivered')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField()),
                ('payment_time', models.DateTimeField(null=True, blank=True)),
                ('method', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pricing',
            fields=[
                ('business', models.OneToOneField(primary_key=True, serialize=False, to='businessapp.Business')),
                ('normal_zone_a_1', models.IntegerField(default=25)),
                ('normal_zone_a_2', models.IntegerField(default=20)),
                ('normal_zone_b_1', models.IntegerField(default=45)),
                ('normal_zone_b_2', models.IntegerField(default=38)),
                ('normal_zone_c_1', models.IntegerField(default=60)),
                ('normal_zone_c_2', models.IntegerField(default=43)),
                ('normal_zone_d_1', models.IntegerField(default=70)),
                ('normal_zone_d_2', models.IntegerField(default=55)),
                ('normal_zone_e_1', models.IntegerField(default=80)),
                ('normal_zone_e_2', models.IntegerField(default=60)),
                ('bulk_zone_a', models.IntegerField(default=13)),
                ('bulk_zone_b', models.IntegerField(default=15)),
                ('bulk_zone_c', models.IntegerField(default=18)),
                ('bulk_zone_d', models.IntegerField(default=20)),
                ('bulk_zone_e', models.IntegerField(default=22)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('price', models.IntegerField(max_length=10, null=True, blank=True)),
                ('weight', models.IntegerField(max_length=10, null=True, blank=True)),
                ('real_tracking_no', models.CharField(max_length=10, null=True, blank=True)),
                ('mapped_tracking_no', models.CharField(max_length=50, null=True, blank=True)),
                ('tracking_data', models.CharField(max_length=8000, null=True, blank=True)),
                ('method', models.CharField(blank=True, max_length=1, null=True, choices=[(b'B', b'Bulk'), (b'N', b'Normal')])),
                ('company', models.CharField(blank=True, max_length=1, null=True, choices=[(b'F', b'FedEx'), (b'D', b'Delhivery')])),
                ('shipping_cost', models.IntegerField(null=True, blank=True)),
                ('date', models.DateTimeField(null=True, blank=True)),
                ('order', models.ForeignKey(blank=True, to='businessapp.Order', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Usernamecheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=100, null=True, blank=True)),
                ('exist', models.CharField(default=b'N', max_length=1, choices=[(b'Y', b'yes'), (b'N', b'no')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='X',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='payment',
            name='business',
            field=models.ForeignKey(to='businessapp.Business'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='business',
            field=models.ForeignKey(to='businessapp.Business'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='loginsession',
            name='Business',
            field=models.ForeignKey(blank=True, to='businessapp.Business', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='business',
            name='businessmanager',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
