# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-15 19:21
from __future__ import unicode_literals

import core.types
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('benchmarks', '0005_auto_20160927_1008'),
        ('portfolios', '0010_auto_20161108_1357'),
        ('securities', '0013_auto_20161114_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='BenchmarkPerformance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('gain', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('cash_flow', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('benchmark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='benchmarks.Benchmark')),
            ],
            options={
                'get_latest_by': 'date',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PortfolioPerformance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('gain', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('cash_flow', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolios.Portfolio')),
            ],
            options={
                'get_latest_by': 'date',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SecurityPerformance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('value', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('gain', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('cash_flow', core.types.DecimalField(decimal_places=28, default=0, max_digits=38)),
                ('security', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='securities.Security')),
            ],
            options={
                'get_latest_by': 'date',
                'abstract': False,
            },
        ),
    ]
