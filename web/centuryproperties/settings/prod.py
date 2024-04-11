from .base import *
import dj_database_url

DEBUG = False

ADMINS = (
    ('Opio Daniel', 'danielopio540@gmail.com'),
)

ALLOWED_HOSTS = ['centuryproperties.pythonanywhere.com']


MEDIA_ROOT = '/home/centuryproperties/management/web/centuryproperties/media/'
MEDIA_URL = '/media/'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}