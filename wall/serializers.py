# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.settings import api_settings

from wall.models import Post, PostLike, User


def jwt_response_payload_handler(token, user=None, request=None):
    """
        Override default rest_framework_jwt handler to return user id
    """
    return {'token': token, 'id': user.id}


# patch default ModelSerializer to return errors if update on read-only field is tried
class ReadOnlyProducesErrorModelSerializer(serializers.ModelSerializer):
    def is_valid(self, raise_exception=False):
        super(ReadOnlyProducesErrorModelSerializer, self).is_valid(raise_exception=raise_exception)
        for k, v in self.initial_data.items():
            if self.fields[k].read_only:
                self._errors[k] = '{} is read-only'.format(k)

        if self._errors and raise_exception:
            raise serializers.ValidationError(self.errors)

        return not bool(self._errors)

serializers.ModelSerializer = ReadOnlyProducesErrorModelSerializer


class UnixEpochDateField(serializers.DateTimeField):
    """
        Retrieved from http://stackoverflow.com/a/28740894
    """
    def to_representation(self, value):
        """ Return epoch time for a datetime object or ``None``"""
        import time
        try:
            return int(time.mktime(value.timetuple()))
        except (AttributeError, TypeError):
            return None

    def to_internal_value(self, value):
        import datetime
        return datetime.datetime.fromtimestamp(int(value))


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'facebook', 'twitter', 'avatar')


class UserSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()

    def get_posts(self, obj):
        """
            Paginate user related posts, show latest first.
            Maybe there is better way to show related data paginated.
        """
        context = self.context
        request = context.get('request')
        if not request:
            return None
        paginator = api_settings.DEFAULT_PAGINATION_CLASS()
        page = paginator.paginate_queryset(obj.posts.order_by('-created'), request)
        serializer = UserDetailPostSerializer(page, many=True, context=context)
        return paginator.get_paginated_response(serializer.data).data

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
            'facebook', 'twitter', 'avatar', 'posts'
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        instance = super(UserSerializer, self).create(validated_data)
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            raise serializers.ValidationError({
                'username': "Can't change username"
            })
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
            del validated_data['password']

        return super(UserSerializer, self).update(instance, validated_data)


class UserBasicData(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class UserDetailPostSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    created = UnixEpochDateField(read_only=True)

    def get_likes(self, obj):
        return obj.likes.count()

    class Meta:
        model = Post
        fields = ('id', 'created', 'post_type', 'text', 'likes')
        read_only_fields = ('id', 'post_type', 'text', 'likes')


class PostCreateSerializer(serializers.ModelSerializer):
    created = UnixEpochDateField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'created', 'post_type', 'author', 'text')
        extra_kwargs = {
            'author': {'required': True},
            'text': {'required': True}
        }


class PostSerializer(serializers.ModelSerializer):
    author = UserBasicData(read_only=True)
    likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    created = UnixEpochDateField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'created', 'author', 'post_type', 'text', 'likes')
        read_only_fields = ('id', 'author', 'post_type')
        extra_kwargs = {
            'text': {'required': True}
        }


class PostLikeSerializer(serializers.ModelSerializer):
    created = UnixEpochDateField(read_only=True)

    class Meta:
        model = PostLike
        fields = ('id', 'post', 'author', 'created')
