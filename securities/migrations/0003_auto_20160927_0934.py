# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-27 09:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('securities', '0002_auto_20160926_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='security',
            name='isindex',
            field=models.BooleanField(default=False, verbose_name='Is this an Index?'),
        ),
    ]