from __future__ import print_function

import re
from collections import defaultdict, OrderedDict
from random import randint, choice

from faker import Faker

from api import API
from config import get_config


class ValidationError(Exception):
    pass


class Bot(object):
    def __init__(self, config=None):
        if not config:
            config = get_config()
        self.config = config
        self.api = API(config.api)

    @staticmethod
    def validate(user_data):
        try:
            all_usernames = []
            for u in user_data:
                for f in ['username', 'email', 'password', 'first_name', 'last_name']:
                    if f not in u:
                        raise ValidationError("{} is required for user".format(f))

                if u['username'] in all_usernames:
                    raise ValidationError("Duplicate user: {}".format(u['username']))

                if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", u['email']):
                    raise ValidationError("Invalid email {}".format(u['email']))

                all_usernames.append(u['username'])

            for u in user_data:
                for p in u.get('posts', []):
                    if 'text' not in p:
                        raise ValidationError("Text is required for post")

        except Exception as e:
            raise ValidationError(e)

    def generate_users_posts(self):
        """
            :returns
            [
                {
                   "username": "bla",
                   "email": "bla@bla.com",
                   "password": "123",
                   "first_name": "John",
                   "last_name": "Doe",
                   "posts": [
                        {
                            "text": "Lorem ipsum"
                        },
                        ...
                   ]
                },
                ...
            ]
        """
        fake = Faker()
        users = []
        usernames = []

        for i in range(self.config.users):
            name = fake.first_name()
            while name in usernames:
                name = fake.first_name()
            user = dict(
                first_name=name, last_name=fake.last_name(),
                username=name.lower(), email=fake.email(), password=fake.password(),
                posts=[]
            )
            for j in range(randint(1, self.config.posts)):
                p = dict(text=fake.text())
                user['posts'].append(p)

            users.append(user)
        return users

    def generate_activity(self, created_users_posts):
        """
            Expects:
            [
                {
                   "username": "bla",
                   "email": "bla@bla.com",
                   "password": "123",
                   "first_name": "John",
                   "last_name": "Doe",
                   "posts": [
                        {   
                            "id": 1
                            "text": "Lorem ipsum"
                        },
                        ...
                   ]
                },
                ...
            ]
        """
        users = []
        users_posts_num_likes = defaultdict(dict)
        post_authors = {}

        for user in created_users_posts:
            for p in user['posts']:
                post_id = p['id']
                users_posts_num_likes[user['username']][post_id] = 0
                post_authors[post_id] = user['username']

                user['likes'] = []
                users.append(user)

        user_map = OrderedDict((u['username'], u) for u in sorted(users, key=lambda u: len(u['posts']), reverse=True))

        for user in user_map.values():
            likes_left = self.config.likes
            post_ids = [k
                        for post_map in users_posts_num_likes.values()
                        for k in post_map.keys() if
                        k not in user['likes']]
            while len(post_ids) and likes_left > 0:
                like_post = choice(post_ids)
                user['likes'].append(like_post)

                like_user = post_authors[like_post]
                users_posts_num_likes[like_user][like_post] += 1
                likes_left -= 1
                if all(nl > 0 for nl in users_posts_num_likes[like_user].values()):
                    del users_posts_num_likes[like_user]
                post_ids = [k
                            for post_map in users_posts_num_likes.values()
                            for k in post_map.keys() if
                            k not in user['likes']]
        return users

    def run(self, user_data=None):
        if not user_data:
            user_data = self.generate_users_posts()

        self.validate(user_data)

        user_apis = []
        for ud in user_data:
            params = ud.copy()
            del params['posts']
            user_api = self.api.register_user(**params)
            user_api.login()
            user_apis.append(user_api)

        print("Registered {} users".format(len(user_data)))

        for api, ud in zip(user_apis, user_data):
            for p in ud['posts']:
                post_id = api.post(p['text'])
                p['id'] = post_id

        user_data = self.generate_activity(user_data)
        for api, ud in zip(user_apis, user_data):
            for l in ud['likes']:
                api.like(l)


if __name__ == '__main__':
    bot = Bot()
    bot.run()
