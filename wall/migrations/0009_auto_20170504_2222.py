# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 22:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wall', '0008_auto_20170504_2017'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='postlike',
            options={'ordering': ('created',)},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('date_joined',)},
        ),
    ]
