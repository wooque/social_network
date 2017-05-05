import os
import unittest
from bot.config import get_config, ConfigError


class TestConfig(unittest.TestCase):

    DEFAULT_CONF = dict(
        api='http://localhost',
        users=3,
        posts=5,
        likes=1
    )

    def write_config(self, config_loc='config.ini', conf=None):
        with open(config_loc, 'w') as c:
            c.write('[conf]\n')
            for k, v in self.DEFAULT_CONF.items():
                if conf and conf.get(k):
                    v = conf[k]
                c.write(k + '=' + str(v) + '\n')

    def test_default_config_loc(self):
        self.write_config()
        config = get_config()
        self.assertEqual(config.api, 'http://localhost')
        self.assertEqual(config.users, 3)
        self.assertEqual(config.posts, 5)
        self.assertEqual(config.likes, 1)

    def test_custom_config_loc_desnt_exist(self):
        with self.assertRaises(ConfigError) as em:
            config_loc = 'bla.ini'
            get_config(config_loc=config_loc)
            self.assertEqual(str(em.exception), "Config file doesn't exists {}".format(config_loc))

    def test_custom_config_loc_exist(self):
        config_loc = 'bla.ini'
        self.write_config(config_loc)
        config = get_config(config_loc=config_loc)
        self.assertEqual(config.api, 'http://localhost')
        self.assertEqual(config.users, 3)
        self.assertEqual(config.posts, 5)
        self.assertEqual(config.likes, 1)

    def test_field_not_int(self):
        value = 'adsads'
        for key in ['users', 'posts', 'likes']:
            self.write_config(conf={key: value})
            with self.assertRaises(ConfigError) as em:
                get_config()
            self.assertEqual(str(em.exception), "{} value is not valid number: {}".format(key, value))

    def test_field_not_in_range(self):
        value = 123123123
        for key in ['users', 'posts', 'likes']:
            self.write_config(conf={key: value})
            with self.assertRaises(ConfigError) as em:
                get_config()
            self.assertEqual(str(em.exception), "{} value should be in range 1-100, value: {}".format(key, value))

    def test_invalid_api_url_schema(self):
        value = 'stf://localhost'
        self.write_config(conf={'api': value})
        with self.assertRaises(ConfigError) as em:
            get_config()
        self.assertEqual(str(em.exception), "Only http and https are supported for api")

    def tearDown(self):
        try:
            os.remove('config.ini')
        except:
            pass
        try:
            os.remove('bla.ini')
        except:
            pass


if __name__ == '__main__':
    unittest.main()
