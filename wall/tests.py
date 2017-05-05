# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestRegister(APITestCase):

    def setUp(self):
        self.params = dict(username='wooque', email='wooque@gmail.com',
                           first_name='Vuk', last_name='Mirovic', password='123')

    def test_register_required_fields(self):
        url = reverse('user-register')
        for k in self.params:
            params = self.params.copy()
            del params[k]
            response = self.client.post(url, params, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(), {k: ['This field is required.']})

    def test_register_simple(self):
        url = reverse('user-register')
        response = self.client.post(url, self.params, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['id'], 1)
        self.assertIn('token', response.json())

    def test_register_double(self):
        url = reverse('user-register')
        self.client.post(url, self.params, format='json')
        response = self.client.post(url, self.params, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['username'], ['A user with that username already exists.'])


class TestLogin(APITestCase):

    def setUp(self):
        register_params = dict(username='wooque', password='123', email='wooque@gmail.com',
                               first_name='Vuk', last_name='Mirovic')
        self.params = dict(username=register_params['username'], password=register_params['password'])

        url = reverse('user-register')
        self.client.post(url, register_params, format='json')
        TestLogin.registered = True

    def test_login_required_fields(self):
        url = reverse('user-login')
        for k in self.params:
            params = self.params.copy()
            del params[k]
            response = self.client.post(url, params, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(), {k: ['This field is required.']})

    def test_login_simple(self):
        url = reverse('user-login')
        response = self.client.post(url, self.params, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], 1)
        self.assertIn('token', response.json())

    def test_login_wrong_credentials(self):
        url = reverse('user-login')
        for k in self.params:
            params = self.params.copy()
            params[k] = 'x'*10
            response = self.client.post(url, params, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(), {'non_field_errors': ['Unable to log in with provided credentials.']})


class TestUserProfile(APITestCase):
    def setUp(self):
        url = reverse('user-register')
        self.user = dict(username='wooque', password='123', email='wooque@gmail.com',
                         first_name='Vuk', last_name='Mirovic')
        self.client.post(url, self.user, format='json')
        url = reverse('user-login')
        login_params = dict(username=self.user['username'], password=self.user['password'])
        response = self.client.post(url, login_params, format='json')
        self.token = response.json()['token']

    def test_user_detail(self):
        url = reverse('user-detail', kwargs=dict(pk=1))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for k in self.user:
            if k == 'password':
                continue
            self.assertEqual(response.json()[k], self.user[k])

    def test_update_user_detail(self):
        url = reverse('user-detail', kwargs=dict(pk=1))
        data = dict(email='hehe@hehe.com', first_name='A', last_name='B', facebook='aaa', twitter='bbb', avatar='ccc')
        for k, v in data.items():
            response = self.client.post(url, {k: v}, format='json')
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            response = self.client.get(url)
            self.assertEqual(response.json()[k], v)

    def test_username_update(self):
        url = reverse('user-detail', kwargs=dict(pk=1))
        response = self.client.post(url, {'username': 'asd'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_update(self):
        new_password = '987'
        url = reverse('user-detail', kwargs=dict(pk=1))
        response = self.client.post(url, {'password': new_password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()
        url = reverse('user-login')
        login_params = dict(username=self.user['username'], password=new_password)
        response = self.client.post(url, login_params, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        url = reverse('user-detail', kwargs=dict(pk=1))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestPosting(APITestCase):
    def setUp(self):
        url = reverse('user-register')
        self.user = dict(username='wooque', password='123', email='wooque@gmail.com',
                         first_name='Vuk', last_name='Mirovic')
        self.client.post(url, self.user, format='json')
        url = reverse('user-login')
        login_params = dict(username=self.user['username'], password=self.user['password'])
        response = self.client.post(url, login_params, format='json')
        self.token = response.json()['token']

    def test_simple(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text='text'), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['id'], 1)

    def test_unauth_post(self):
        self.client.logout()
        url = reverse('post-list')
        response = self.client.post(url, dict(text='text'), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text=''), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['text'], ['This field may not be blank.'])

    def test_unicode(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text='ћирилица'), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_long(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text='a'*100000), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['text'], [u'Ensure this field has no more than 16384 characters.'])

    def test_update_text(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text='text'), format='json')
        post_id = response.json()['id']
        url = reverse('post-detail', kwargs=dict(pk=post_id))
        response = self.client.post(url, dict(text='abc'), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_read_only(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text='text'), format='json')
        post_id = response.json()['id']
        url = reverse('post-detail', kwargs=dict(pk=post_id))
        for k, v in dict(created=123, author={'id': 3}, post_type=1, id=3, likes=[]).items():
            response = self.client.post(url, {k: v}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, "{} updated!".format(k))
            self.assertEqual(response.json()[k], '{} is read-only'.format(k))

    def test_delete(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text='text'), format='json')
        post_id = response.json()['id']
        url = reverse('post-detail', kwargs=dict(pk=post_id))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauth_update(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text='text'), format='json')
        post_id = response.json()['id']
        url = reverse('post-detail', kwargs=dict(pk=post_id))
        self.client.logout()
        response = self.client.post(url, dict(text='abc'), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_author_update(self):
        url = reverse('post-list')
        response = self.client.post(url, dict(text='text'), format='json')
        post_id = response.json()['id']
        self.client.logout()

        # register second user
        url = reverse('user-register')
        user = dict(username='wooque2', password='123', email='wooque2@gmail.com',
                    first_name='Vuk', last_name='Mirovic')
        self.client.post(url, user, format='json')
        url = reverse('user-login')
        login_params = dict(username=user['username'], password=user['password'])
        self.client.post(url, login_params, format='json')

        url = reverse('post-detail', kwargs=dict(pk=post_id))
        response = self.client.post(url, dict(text='abc'), format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLike(APITestCase):
    def setUp(self):
        url = reverse('user-register')
        self.user = dict(username='wooque', password='123', email='wooque@gmail.com',
                         first_name='Vuk', last_name='Mirovic')
        self.client.post(url, self.user, format='json')

        url = reverse('user-login')
        login_params = dict(username=self.user['username'], password=self.user['password'])
        response = self.client.post(url, login_params, format='json')
        self.token = response.json()['token']

        url = reverse('post-list')
        response = self.client.post(url, dict(text='text'), format='json')
        post_id = response.json()['id']

        self.like_url = reverse('post-like', kwargs=dict(pk=post_id))

    def test_like(self):
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_double_like(self):
        self.client.post(self.like_url)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unlike(self):
        self.client.post(self.like_url)
        response = self.client.delete(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauth_like(self):
        self.client.logout()
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
