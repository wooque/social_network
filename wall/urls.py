from django.conf.urls import url

from wall import views


urlpatterns = [
    url(r'^posts/$', views.PostListCreateView.as_view(), name='post-list'),
    url(r'^posts/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='post-detail'),
    url(r'^posts/(?P<pk>[0-9]+)/like/$', views.PostLikeView.as_view(), name='post-like'),
    url(r'^users/$', views.UserListView.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetailView.as_view(), name='user-detail'),
    url(r'^users/(?P<pk>[0-9]+)/posts/$', views.UserPostListView.as_view(), name='user-posts-list'),
]
