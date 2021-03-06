# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-27 09:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('securities', '0005_auto_20161027_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='securityinfo',
            name='outstanding_shares',
            field=models.FloatField(null=True, verbose_name='Outstanding Shares'),
        ),
        migrations.AlterField(
            model_name='securityinfo',
            name='total_shares',
            field=models.FloatField(null=True, verbose_name='Total Shares'),
        ),
    ]
