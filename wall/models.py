# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User as DjangoUser


class User(DjangoUser):
    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    facebook = models.CharField(max_length=1024, blank=True, default='')
    twitter = models.CharField(max_length=1024, blank=True, default='')
    avatar = models.CharField(max_length=1024, blank=True, default='')

    class Meta:
        ordering = ('date_joined',)


class Post(models.Model):

    POST_TYPES = ((0, 'text'), (1, 'url'),)

    created = models.DateTimeField(auto_now_add=True)
    # delete all posts if user is deleted
    author = models.ForeignKey('auth.User', related_name='posts', on_delete=models.CASCADE)
    post_type = models.IntegerField(choices=POST_TYPES, blank=True, default=0)
    text = models.CharField(max_length=16*1024)

    class Meta:
        ordering = ('created',)


class PostLike(models.Model):
    post = models.ForeignKey('wall.Post', related_name='likes')
    # delete all likes if post is deleted
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("post", "author"),)
        ordering = ('created',)
