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
                ('Phone', models.CharField(max_length=50)),
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
                ('Business', models.ForeignKey(blank=True, to='businessapp.Business', null=True)),
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
                ('business', models.ForeignKey(to='businessapp.Business')),
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
                ('business', models.ForeignKey(to='businessapp.Business')),
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
                ('price', models.CharField(max_length=10, null=True, blank=True)),
                ('weight', models.CharField(max_length=10, null=True, blank=True)),
                ('real_tracking_no', models.CharField(max_length=10, null=True, blank=True)),
                ('mapped_tracking_no', models.CharField(max_length=50, null=True, blank=True)),
                ('tracking_data', models.CharField(max_length=8000, null=True, blank=True)),
                ('company', models.CharField(blank=True, max_length=1, null=True, choices=[(b'F', b'FedEx'), (b'D', b'Delhivery')])),
                ('order', models.ForeignKey(to='businessapp.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='business',
            name='businessmanager',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
