"""
Django settings for pokemondraftleague project.

Generated by 'django-admin startproject' using Django 1.11.20.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys
import socket

if (socket.gethostname().find("local")>-1):
    from .base_settings import *
    DEBUG = True
    SECRET_KEY = SECRET_KEY
    SENDGRID_API_KEY = SENDGRID_API_KEY
    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME
    NAME=NAME
    USER=USER
    PASSWORD=PASSWORD
    HOST=HOST
else:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY','developmentkey')
    SENDGRID_API_KEY= os.environ.get('SENDGRID_API_KEY')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    DATABASE_URL = os.environ.get('DATABASE_URL','postgres://user:password@host:port/database')
    NAME=DATABASE_URL.split("/")[-1]
    USER=DATABASE_URL.split("//")[1].split(":")[0]
    PASSWORD=DATABASE_URL.split("//")[1].split(":")[1].split("@")[0]
    HOST=DATABASE_URL.split("//")[1].split(":")[1].split("@")[1]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
ALLOWED_HOSTS = ['0.0.0.0',"pokemondraftleague.herokuapp.com",'127.0.0.1',"pokemondraftleague.online"]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    #local apps
    'accounts.apps.AccountsConfig',
    'leagues.apps.LeaguesConfig',
    'main.apps.MainConfig',
    'pokemoninfo.apps.PokemoninfoConfig',

    #third party apps
    'crispy_forms',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #third-party middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'pokemondraftleague.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates"),os.path.join(BASE_DIR,"accounts/templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                #custom
                'pokemondraftleague.processors.processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'pokemondraftleague.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': NAME,                      
        'USER': USER,
        'PASSWORD': PASSWORD,
        'HOST': HOST,
        'PORT': '5432',
        'TEST': {
          'NAME': 'testdb',
        }
    },
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#other settings
LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'home'

#Crispy Forms Settings
CRISPY_TEMPLATE_PACK = 'bootstrap4'

#Sendgrid Settings
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "accounts/sent_emails")
SENDGRID_SANDBOX_MODE_IN_DEBUG=False
EMAIL_USE_TLS= True
DEFAULT_FROM_EMAIL='pokemondraftleagueonline@gmail.com'

#AWS SETTINGS
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_DEFAULT_ACL = None

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'pokemondraftleague/staticfiles')
STATIC_URL = '/static/' 
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

#Media files
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'pokemondraftleague.storage_backends.PublicMediaStorage'