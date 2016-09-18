# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-18 12:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField()),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('inactive', 'Inactive'), ('active', 'Active'), ('done', 'Done')], max_length=10)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='todos.Todo')),
            ],
        ),
    ]
