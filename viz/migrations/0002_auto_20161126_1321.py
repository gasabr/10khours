# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-26 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viz', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='calendarmodel',
            old_name='calendar_id',
            new_name='name',
        ),
        migrations.AlterField(
            model_name='calendarmodel',
            name='id',
            field=models.CharField(max_length=150, primary_key=True, serialize=False),
        ),
    ]
