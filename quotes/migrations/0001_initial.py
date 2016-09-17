# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-15 15:55
from __future__ import unicode_literals

import core.types
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('securities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('open', core.types.PositiveDecimalField(decimal_places=28, max_digits=38)),
                ('close', core.types.PositiveDecimalField(decimal_places=28, max_digits=38)),
                ('high', core.types.PositiveDecimalField(decimal_places=28, max_digits=38)),
                ('low', core.types.PositiveDecimalField(decimal_places=28, max_digits=38)),
                ('volume', core.types.PositiveDecimalField(decimal_places=28, max_digits=38)),
                ('security', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotes', to='securities.Security')),
            ],
        ),
    ]