# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-02 09:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('portfolios', '0008_portfolio_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolio',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='portfolio',
            unique_together=set([('name', 'owner')]),
        ),
    ]