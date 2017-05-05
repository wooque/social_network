import os
import multiprocessing
import signal
import time
import unittest

import django
from django.core.management import call_command

from bot.config import Config
from bot.bot import Bot, ValidationError


class TestBotGenerateData(unittest.TestCase):

    def test_generate_users_posts_data(self):
        bot = Bot()
        users = bot.generate_users_posts()
        self.assertEqual(len(users), bot.config.users)
        for u in users:
            self.assertEqual(sorted(u.keys()),
                             sorted(['username', 'email', 'password', 'first_name', 'last_name', 'posts']))
            self.assertLessEqual(len(u['posts']), bot.config.posts)
            for p in u.get('posts', []):
                self.assertEqual(p.keys(), ['text'])


class TestBotValidate(unittest.TestCase):

    def setUp(self):
        self.params = {
            'username': 'bla',
            'email': 'bla@bla.com',
            'password': '123',
            'first_name': '123',
            'last_name': '123',
            'posts': [{'text': 'test', 'likes': ['bla']}]
        }

    def test_skip_required(self):
        for k in ['username', 'email', 'password', 'first_name', 'last_name']:
            with self.assertRaises(ValidationError) as cm:
                c_params = self.params.copy()
                del c_params[k]
                Bot.validate([c_params])
            self.assertEqual(str(cm.exception), '{} is required for user'.format(k))

    def test_duplicate_user(self):
        with self.assertRaises(ValidationError) as cm:
            Bot.validate([self.params, self.params])
        self.assertEqual(str(cm.exception), 'Duplicate user: {}'.format(self.params['username']))

    def test_invalid_email(self):
        self.params['email'] = 'qwe'
        with self.assertRaises(ValidationError) as cm:
            Bot.validate([self.params])
        self.assertEqual(str(cm.exception), 'Invalid email qwe')

    def test_validate_post_without_text(self):
        del self.params['posts'][0]['text']
        with self.assertRaises(ValidationError) as cm:
            Bot.validate([self.params])
        self.assertEqual(str(cm.exception), 'Text is required for post')


class TestBot(unittest.TestCase):
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

    def test_simple(self):
        bot = Bot(Config(api='http://127.0.0.1:8000', users=5, posts=3, likes=2))
        bot.run()

    # TODO: check if bot really created users/posts/likes

    @classmethod
    def tearDownClass(cls):
        # stop Django REST server and clean DB
        if cls.pid:
            os.kill(cls.pid, signal.SIGTERM)
        os.remove('test.db')


if __name__ == '__main__':
    unittest.main()
