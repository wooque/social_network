# coding=utf-8
import multiprocessing
import os
import signal
import time
import unittest
import random
import string

import django
from django.core.management import call_command

from bot.api import API, APIError, AuthenticatedError


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # remove leftovers
        try:
            os.remove('test.db')
        except:
            pass

        # setup test DB
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_network.settings.test")
        django.setup()
        call_command('migrate')

        # start Django REST server
        p = multiprocessing.Process(target=call_command, args=('runserver', '--noreload'))
        p.daemon = True
        p.start()
        cls.pid = p.pid
        time.sleep(2)

    def setUp(self):
        self.api = API(host='http://127.0.0.1:8000')
        self.params = dict(username='wooque', email='wooque@gmail.com',
                           password='bla', first_name='Vuk', last_name='Mirovic')

    def register(self):
        rand_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.params['username'] = rand_str + "@gmail.com"
        self.params['email'] = rand_str + "@gmail.com"
        return self.api.register_user(**self.params)

    def register_and_login(self):
        user = self.register()
        user.login()
        return user

    def test_register(self):
        user = self.api.register_user(**self.params)
        self.assertEqual(user.username, self.params['username'])
        self.assertEqual(user.email, self.params['email'])
        self.assertEqual(user.password, self.params['password'])
        self.assertEqual(user.first_name, self.params['first_name'])
        self.assertEqual(user.last_name, self.params['last_name'])
        self.assertIsNotNone(user.id)
        self.assertIsNone(user.api.token)

    def test_register_same(self):
        with self.assertRaises(APIError) as cm:
            self.api.register_user(**self.params)
        self.assertEquals(cm.exception.status, 400)

    def test_post_not_logged_in(self):
        user = self.register()
        with self.assertRaises(AuthenticatedError):
            user.post('test')

    def test_like_not_logged_in(self):
        user = self.register()
        with self.assertRaises(AuthenticatedError):
            user.like(123)

    def test_login(self):
        user = self.register_and_login()
        self.assertIsNotNone(user.api.token)

    def test_post_empty(self):
        user = self.register_and_login()
        with self.assertRaises(APIError) as cm:
            user.post('')
        self.assertEqual(cm.exception.status, 400)

    def test_post_simple(self):
        user = self.register_and_login()
        user.post(text='test')

    def test_post_unicode(self):
        user = self.register_and_login()
        user.post(text=u'ћирилица')

    def test_post_long_post(self):
        user = self.register_and_login()
        with self.assertRaises(APIError) as cm:
            user.post(text='a'*100000)
        self.assertEqual(cm.exception.status, 400)

    def test_like_post_doesnt_exist(self):
        user = self.register_and_login()
        with self.assertRaises(APIError) as cm:
            user.like(123456)
        self.assertEqual(cm.exception.status, 400)

    def test_like_simple(self):
        user = self.register_and_login()
        post = user.post('text')
        user.like(post)

    @classmethod
    def tearDownClass(cls):
        # stop Django REST server and clean DB
        if cls.pid:
            os.kill(cls.pid, signal.SIGTERM)
        os.remove('test.db')


if __name__ == '__main__':
    unittest.main()
