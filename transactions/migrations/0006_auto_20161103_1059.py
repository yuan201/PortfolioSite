# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-03 10:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0005_auto_20161103_1057'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='transaction2',
            unique_together=set([]),
        ),
    ]
