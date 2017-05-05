import os
from collections import namedtuple
from ConfigParser import ConfigParser
from urlparse import urlparse

# Bot config
Config = namedtuple('Config', ['api', 'users', 'posts', 'likes'])


class ConfigError(Exception):
    pass


def get_config(config_loc=None):
    """
        Loads Bot config from ini file, if none provided it will look by default to config.ini
    """
    if not config_loc:
        config_loc = 'config.ini'
    else:
        if not os.path.exists(config_loc):
            raise ConfigError("Config file doesn't exists {}".format(config_loc))

    config = dict(api="http://127.0.0.1:8080", users=5, posts=3, likes=2)

    parser = ConfigParser()
    parser.read(config_loc)

    for k in config:
        try:
            value = parser.get('conf', k)
            if k in ['users', 'posts', 'likes']:
                try:
                    value = int(value)
                except:
                    raise ConfigError("{} value is not valid number: {}".format(k, value))

                if value <= 0 or value > 100:
                    raise ConfigError("{} value should be in range 1-100, value: {}".format(k, value))

            if k == 'api':
                parsed_url = urlparse(value)
                if parsed_url.scheme == '':
                    value = "http://" + value

                elif parsed_url.scheme not in ['http', 'https']:
                    raise ConfigError("Only http and https are supported for api")

            config[k] = value
        except ConfigError:
            raise
        except:
            pass

    return Config(**config)
