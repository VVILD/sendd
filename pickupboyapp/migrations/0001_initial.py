# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PBLocations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PBPincodes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pincode', models.CharField(max_length=30, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PBUser',
            fields=[
                ('phone', models.CharField(max_length=10, serialize=False, primary_key=True, validators=[django.core.validators.RegexValidator(regex=b'^[0-9]*$', message=b"Phone number must be entered in the format: '999999999'. Up to 12 digits allowed.")])),
                ('name', models.CharField(max_length=100)),
                ('otp', models.IntegerField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image_url', models.CharField(max_length=255, null=True, blank=True)),
                ('doc_url', models.CharField(max_length=255, null=True, blank=True)),
                ('status', models.CharField(default=b'A', max_length=1, choices=[(b'A', b'Active'), (b'T', b'Terminated'), (b'V', b'Vacation'), (b'S', b'Sabbatical')])),
                ('pincodes', models.ManyToManyField(to='pickupboyapp.PBPincodes')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pblocations',
            name='pbuser',
            field=models.ForeignKey(to='pickupboyapp.PBUser'),
            preserve_default=True,
        ),
    ]
