# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-11 00:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('performances', '0002_auto_20170220_1412'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='portfolioperformance',
            options={'get_latest_by': 'date'},
        ),
    ]