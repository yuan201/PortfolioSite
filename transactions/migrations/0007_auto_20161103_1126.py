# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-03 11:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0006_auto_20161103_1059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buytransaction',
            name='portfolio',
        ),
        migrations.RemoveField(
            model_name='buytransaction',
            name='security',
        ),
        migrations.RemoveField(
            model_name='dividendtransaction',
            name='portfolio',
        ),
        migrations.RemoveField(
            model_name='dividendtransaction',
            name='security',
        ),
        migrations.RemoveField(
            model_name='selltransaction',
            name='portfolio',
        ),
        migrations.RemoveField(
            model_name='selltransaction',
            name='security',
        ),
        migrations.RemoveField(
            model_name='splittransaction',
            name='portfolio',
        ),
        migrations.RemoveField(
            model_name='splittransaction',
            name='security',
        ),
        migrations.DeleteModel(
            name='BuyTransaction',
        ),
        migrations.DeleteModel(
            name='DividendTransaction',
        ),
        migrations.DeleteModel(
            name='SellTransaction',
        ),
        migrations.DeleteModel(
            name='SplitTransaction',
        ),
    ]
