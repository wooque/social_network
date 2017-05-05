# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
import logging

from django.conf import settings
from django.db import IntegrityError
from rest_framework import permissions, status, exceptions, views, generics, mixins
from rest_framework.response import Response
from rest_framework_jwt.views import JSONWebTokenSerializer, api_settings


from wall.models import Post, PostLike, User
from wall.serializers import PostSerializer, PostCreateSerializer, \
    UserSerializer, UserListSerializer, PostLikeSerializer
from wall.permissions import IsAuthorOrReadOnly, UserPermission
from wall.email_checker import check_email
from wall.tasks import load_additional_user_data


logger = logging.getLogger()


class UserRegisterView(views.APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        # reject accounts with scamy emails
        email = serializer.validated_data['email']
        if not check_email(email):
            raise exceptions.ValidationError("Invalid email")

        try:
            serializer.save()
        except IntegrityError:
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # fetch additional data about users, like facebook, twitter profiles, avatar, etc
        if settings.ENRICH_USER_DATA:
            try:
                load_additional_user_data.delay(email)
            except:
                logger.error("Celery is unavailable")

        # authenticate and return token
        jwt_ser = JSONWebTokenSerializer(data=request.data)
        if jwt_ser.is_valid():
            response = Response(
                {'token': jwt_ser.object['token'], 'id': serializer.data['id']},
                status=status.HTTP_201_CREATED
            )
            if api_settings.JWT_AUTH_COOKIE:
                expiration = datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
                response.set_cookie(api_settings.JWT_AUTH_COOKIE, response.data['token'],
                                    expires=expiration, httponly=True)
            return response

        return Response({'id': serializer.data['id']}, status=status.HTTP_201_CREATED)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer


class UserDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin, generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, UserPermission,)

    def post(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPostListView(generics.ListAPIView):
    """
        Posts of single user
    """
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Post.objects.filter(author=self.kwargs['pk'])


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        else:
            return PostSerializer

    def post(self, request, *args, **kwargs):
        request.data['author'] = request.user.pk
        response = super(PostListCreateView, self).create(request, *args, **kwargs)
        return Response({'id': response.data['id']}, status=response.status_code)


class PostDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin, generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)

    def post(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostLikeView(generics.CreateAPIView, generics.DestroyAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return PostLike.objects.filter(post=self.kwargs['pk'], author=self.request.user.pk)

    def create(self, request, *args, **kwargs):
        request.data['author'] = request.user.pk
        request.data['post'] = kwargs['pk']
        return super(PostLikeView, self).create(request, *args, **kwargs)
