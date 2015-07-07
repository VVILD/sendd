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
            name='Billing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('username', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('apikey', models.CharField(max_length=100, null=True, blank=True)),
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
            name='Changepass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('changed', models.CharField(default=b'N', max_length=1, choices=[(b'Y', b'yes'), (b'N', b'no')])),
                ('time', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Forgotpass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('auth', models.CharField(max_length=80, null=True, blank=True)),
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
                ('msg', models.CharField(default=b'wrongpassword', max_length=100, choices=[(b'notregistered', b'notregistered'), (b'wrongpassword', b'wrongpassword'), (b'success', b'success')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('reference_id', models.CharField(max_length=100, null=True, blank=True)),
                ('order_no', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('phone', models.CharField(max_length=12)),
                ('email', models.EmailField(max_length=75, null=True, blank=True)),
                ('address1', models.CharField(max_length=300, null=True, blank=True)),
                ('address2', models.CharField(max_length=300, null=True, blank=True)),
                ('city', models.CharField(max_length=50, null=True, blank=True)),
                ('state', models.CharField(max_length=50, null=True, blank=True)),
                ('pincode', models.CharField(max_length=30, null=True, blank=True)),
                ('country', models.CharField(max_length=30, null=True, blank=True)),
                ('payment_method', models.CharField(max_length=1, choices=[(b'F', b'free checkout'), (b'C', b'cod')])),
                ('book_time', models.DateTimeField(null=True, blank=True)),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'P', b'pending'), (b'C', b'complete'), (b'N', b'cancelled'), (b'D', b'delivered')])),
                ('method', models.CharField(blank=True, max_length=1, null=True, choices=[(b'B', b'Bulk'), (b'N', b'Normal')])),
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
            name='Pricing',
            fields=[
                ('business', models.OneToOneField(primary_key=True, serialize=False, to='businessapp.Business')),
                ('normal_zone_a_0', models.FloatField(default=12)),
                ('normal_zone_a_1', models.FloatField(default=15)),
                ('normal_zone_a_2', models.FloatField(default=13)),
                ('normal_zone_b_0', models.FloatField(default=16)),
                ('normal_zone_b_1', models.FloatField(default=30)),
                ('normal_zone_b_2', models.FloatField(default=26)),
                ('normal_zone_c_0', models.FloatField(default=24)),
                ('normal_zone_c_1', models.FloatField(default=33)),
                ('normal_zone_c_2', models.FloatField(default=32)),
                ('normal_zone_d_0', models.FloatField(default=24)),
                ('normal_zone_d_1', models.FloatField(default=40)),
                ('normal_zone_d_2', models.FloatField(default=38)),
                ('normal_zone_e_0', models.FloatField(default=38)),
                ('normal_zone_e_1', models.FloatField(default=48)),
                ('normal_zone_e_2', models.FloatField(default=45)),
                ('bulk_zone_a', models.FloatField(default=8)),
                ('bulk_zone_b', models.FloatField(default=9.5)),
                ('bulk_zone_c', models.FloatField(default=11)),
                ('bulk_zone_d', models.FloatField(default=13)),
                ('bulk_zone_e', models.FloatField(default=15)),
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
            model_name='forgotpass',
            name='business',
            field=models.ForeignKey(to='businessapp.Business'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='changepass',
            name='business',
            field=models.ForeignKey(to='businessapp.Business'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='business',
            name='businessmanager',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='billing',
            name='business',
            field=models.ForeignKey(blank=True, to='businessapp.Business', null=True),
            preserve_default=True,
        ),
    ]
