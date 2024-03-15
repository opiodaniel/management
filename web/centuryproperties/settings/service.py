from .base import *
import dj_database_url

DEBUG = True

ADMINS = (
    ('Opio Daniel', 'danielopio540@gmail.com'),
)

ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'acDantez',
        'USER': 'opio',
        'PASSWORD': 'sql1passq',
        'HOST': 'acdantez.clgqa6mksciw.us-east-1.rds.amazonaws.com',
        'PORT': 5432
    }
}


MEDIA_ROOT = '/home/opio/projects/management/web/centuryproperties/media/'  # for nginx
STATIC_ROOT = '/home/opio/projects/management/web/static/'  # for nginx

AWS_ACCESS_KEY_ID = 'AKIARK6LB2IT4PPO7SHH'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'acdantez'
AWS_S3_SIGNATURE_NAME = 's3v4',
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERITY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
