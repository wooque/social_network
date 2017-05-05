# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 22:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wall', '0006_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='facebook',
            field=models.CharField(blank=True, default='', max_length=16384),
        ),
        migrations.AddField(
            model_name='user',
            name='google',
            field=models.CharField(blank=True, default='', max_length=16384),
        ),
        migrations.AddField(
            model_name='user',
            name='linkedin',
            field=models.CharField(blank=True, default='', max_length=16384),
        ),
        migrations.AddField(
            model_name='user',
            name='twitter',
            field=models.CharField(blank=True, default='', max_length=16384),
        ),
    ]