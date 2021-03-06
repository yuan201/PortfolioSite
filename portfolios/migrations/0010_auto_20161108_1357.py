# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-08 13:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('securities', '0009_auto_20161031_1050'),
        ('portfolios', '0009_auto_20161002_0927'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='holding',
            options={'get_latest_by': 'date'},
        ),
        migrations.AlterField(
            model_name='holding',
            name='portfolio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='holdings', to='portfolios.Portfolio'),
        ),
        migrations.AlterUniqueTogether(
            name='holding',
            unique_together=set([('security', 'portfolio', 'date')]),
        ),
    ]
