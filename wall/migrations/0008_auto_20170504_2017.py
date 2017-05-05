# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wall', '0007_auto_20170502_2233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='google',
        ),
        migrations.RemoveField(
            model_name='user',
            name='linkedin',
        ),
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='post',
            name='post_type',
            field=models.IntegerField(blank=True, choices=[(0, 'text'), (1, 'url')], default=0),
        ),
        migrations.AlterField(
            model_name='user',
            name='facebook',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='user',
            name='twitter',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
    ]
