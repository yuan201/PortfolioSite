# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-11 00:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('securities', '0014_auto_20170311_0057'),
        ('quotes', '0003_auto_20161031_1006'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='quote',
            unique_together=set([('security', 'date')]),
        ),
    ]
