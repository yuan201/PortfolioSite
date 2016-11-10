# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-10 10:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('securities', '0010_auto_20161110_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='exchange',
            field=models.CharField(blank=True, choices=[('SSE', 'Shanghai Stock Exchange'), ('SZSE', 'Shenzhen Stock Exchange'), ('NYSE', 'Newyork Stock Exchange'), ('NASDAQ', 'Nasdaq Stock Market')], max_length=20, null=True),
        ),
    ]