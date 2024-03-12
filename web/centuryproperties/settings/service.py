from .base import *
import dj_database_url

DEBUG = False

ADMINS = (
    ('Opio Daniel', 'danielopio540@gmail.com'),
)

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'acDantez',
        'USER': 'opio',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'acdantez.clgqa6mksciw.us-east-1.rds.amazonaws.com',
        'PORT': 5432
    }
}

MEDIA_ROOT = '/home/opio/projects/management/web/centuryproperties/media/'  # for nginx
STATIC_ROOT = '/home/opio/projects/management/web/static/'  # for nginx

