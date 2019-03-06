# encoding=utf-8

import os

# # This is the 'code' that was snail-mailed via postcard to the possible participants for the events
# # User has to enter it before they can start register themselves.
# INITIAL_REGISTRATION_KEY = "0109"



# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_PATH = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nv8^dhq#e#-8lsl1z7xc2@0e#ou9k&4@5^*e1am(0q=ue-%9wj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# TODO(dkg): set this to a better value on the prod server
ALLOWED_HOSTS = ['*']


MANAGERS = ADMINS

FROM_EMAIL = "daniel.kurashige@t-mark.co.jp"

XLS_FORMAT = 'M d Y h:i A'

HOST = "localhost:8000"
HOST_URL = "http://%s" % HOST

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATIC_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, "../static/"))
MEDIA_ROOT = os.path.abspath(os.path.join(CURRENT_PATH, "../media"))

ADMIN_REORDER = (
    ("invitationform", ("EventForm2019", "EventForm", "Events")),
)



# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'invitationform',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'concertinvitation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.abspath(os.path.join(CURRENT_PATH, 'templates/'))
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.csrf',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'concertinvitation.wsgi.application'


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

LANGUAGE_CODE = 'ja-ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


try:
    from local_settings import *
except ImportError:
    print "Could not import local_settings.py"
    pass

if not os.path.exists(STATIC_ROOT):
    print "WARNING! STATIC_ROOT does not exists: %s" % (STATIC_ROOT)
if not os.path.exists(MEDIA_ROOT):
    print "WARNING! MEDIA_ROOT does not exists: %s" % (MEDIA_ROOT)
