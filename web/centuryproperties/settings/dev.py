from .base import *
import dj_database_url

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


# if 'DATABASE_URL' in os.environ:
#     DATABASES['default'] = dj_database_url.config(
#         conn_max_age=500,
#         conn_health_checks=True,
#     )
