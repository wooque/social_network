# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 21:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wall', '0004_auto_20170502_2035'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='postlike',
            unique_together=set([('post', 'author')]),
        ),
    ]
