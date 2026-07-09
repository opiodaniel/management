import os

from .base import *
import dj_database_url

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
# DEBUG = False
ADMINS = (
    ('', ''),
)

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    },
}

database_url = os.environ.get("DATABASE_URL")
DATABASES['default'] = dj_database_url.parse(database_url)

settings = os.environ.get('DJANGO_SETTINGS_MODULE')

MEDIA_ROOT = '/home/opio/projects/management/web/centuryproperties/media/'



if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

