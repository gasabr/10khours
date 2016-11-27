# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-24 18:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import oauth2client.contrib.django_util.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CredentialsModel',
            fields=[
                ('credentials', oauth2client.contrib.django_util.models.CredentialsField(null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'credentials',
            },
        ),
    ]