# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-27 10:08
from __future__ import unicode_literals

import core.types
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('benchmarks', '0004_benchmarkperformance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='benchmarkconstitute',
            name='percent',
            field=core.types.PositiveDecimalField(decimal_places=28, max_digits=38),
        ),
    ]
