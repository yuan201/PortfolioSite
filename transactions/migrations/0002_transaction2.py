# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-02 13:15
from __future__ import unicode_literals

import core.types
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolios', '0009_auto_20161002_0927'),
        ('securities', '0009_auto_20161031_1050'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('type', models.CharField(choices=[('buy', 'Buy'), ('sell', 'Sell'), ('div', 'Dividend'), ('split', 'Split')], max_length=10)),
                ('price', core.types.PositiveDecimalField(blank=True, decimal_places=28, default=0, max_digits=38, null=True)),
                ('shares', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('fee', core.types.PositiveDecimalField(blank=True, decimal_places=28, default=0, max_digits=38, null=True)),
                ('dividend', core.types.PositiveDecimalField(blank=True, decimal_places=28, default=0, max_digits=38, null=True)),
                ('ratio', core.types.PositiveDecimalField(blank=True, decimal_places=28, default=0, max_digits=38, null=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolios.Portfolio')),
                ('security', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='securities.Security')),
            ],
            options={
                'get_latest_by': 'datetime',
                'ordering': ['-datetime'],
            },
        ),
    ]
