# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-03 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_auto_20161103_0819'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction2',
            options={'get_latest_by': 'datetime', 'ordering': ['datetime']},
        ),
        migrations.AlterField(
            model_name='transaction2',
            name='type',
            field=models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell'), ('dividend', 'Dividend'), ('split', 'Split')], max_length=10),
        ),
    ]
