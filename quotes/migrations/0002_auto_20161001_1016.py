# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-01 10:16
from __future__ import unicode_literals

import core.types
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='close',
            field=core.types.PositiveDecimalField(decimal_places=28, default=0, max_digits=38),
        ),
        migrations.AlterField(
            model_name='quote',
            name='high',
            field=core.types.PositiveDecimalField(decimal_places=28, default=0, max_digits=38),
        ),
        migrations.AlterField(
            model_name='quote',
            name='low',
            field=core.types.PositiveDecimalField(decimal_places=28, default=0, max_digits=38),
        ),
        migrations.AlterField(
            model_name='quote',
            name='open',
            field=core.types.PositiveDecimalField(decimal_places=28, default=0, max_digits=38),
        ),
        migrations.AlterField(
            model_name='quote',
            name='volume',
            field=core.types.PositiveDecimalField(decimal_places=28, default=0, max_digits=38),
        ),
    ]
