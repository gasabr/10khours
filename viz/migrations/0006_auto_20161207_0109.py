# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-06 22:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viz', '0005_delete_periodmanager'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('icaluid', models.CharField(max_length=100)),
                ('summary', models.CharField(max_length=150)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('duration', models.DurationField()),
                ('update_time', models.DateTimeField()),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viz.CalendarModel')),
            ],
        ),
        migrations.RemoveField(
            model_name='periodmodel',
            name='calendar',
        ),
        migrations.DeleteModel(
            name='PeriodModel',
        ),
    ]
