from .base import *


DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'centuryproperties',
        'USER': 'centuryproperties',
        'PASSWORD': 'sql1passq',
        'HOST': 'localhost',
        'PORT': 5432
    }
}


