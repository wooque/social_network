from social_network.settings.base import *

CHECK_EMAIL = False
ENRICH_USER_DATA = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db'
    }
}
