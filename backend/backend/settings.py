"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from kombu import Queue

from . import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.DEBUG

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'crispy_forms',  # add django template cache before deployment
    'mathfilters',

    'regulation',
    'biobricks',
    'data_wrapper',
    'cobra_wrapper.apps.CobraWrapperConfig',
    'share',
    'bigg_database',
    'accounts',
    'search'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

if config.USE_MYSQL:
    mysql_host = "127.0.0.1"
    if config.MYSQL_HOST:
        mysql_host = config.MYSQL_HOST
    # Testing mysql
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'igem_backend',
            'USER': config.MYSQL_USER,
            'PASSWORD': config.MYSQL_PASSWORD,
            'HOST': mysql_host,
            'PORT': config.MYSQL_PORT,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Postgresql Database
# Used for search
PSQL_DATABASE = {
    'USER': config.PSQL_USER,
    'PASSWORD': config.PSQL_PASSWORD,
    'NAME': 'igem_backend',
    'HOST': config.PSQL_HOST
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = config.STATIC_ROOT

if DEBUG:
    CORS_ORIGIN_ALLOW_ALL = True
    DATA_UPLOAD_MAX_NUMBER_FIELDS = None
else:
    CORS_ORIGIN_WHITELIST = [
        "http://127.0.0.1:8080"  # for testing purpose (vue-cli project)
    ]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' \
    if config.USE_EMAIL else 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = config.EMAIL_HOST
EMAIL_PORT = config.EMAIL_PORT
EMAIL_HOST_USER = config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL = config.DEFAULT_FROM_EMAIL

CELERY_BROKER_URL = config.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ROUTES = {
    'cobra_computation.tasks.cobra_fba': {
        'queue': 'cobra_feeds',
        'routing_key': 'cobra_feed.fba',
    },
    'cobra_wrapper.tasks.cobra_fba_save': {
        'queue': 'cobra_results',
        'routing_key': 'cobra_result.fba',
    },
    'cobra_computation.tasks.cobra_fva': {
        'queue': 'cobra_feeds',
        'routing_key': 'cobra_feed.fva',
    },
    'cobra_wrapper.tasks.cobra_fva_save': {
        'queue': 'cobra_results',
        'routing_key': 'cobra_result.fva',
    },
    'regulation.tasks.gene_regulation': {
        'queue': 'cobra_locals',
        'routing_key': 'cobra_local.regulation',
    },
}
CELERY_TASK_QUEUES = (
    Queue('default', routing_key='task.#'),
    Queue('cobra_feeds', routing_key='cobra_feed.#'),
    Queue('cobra_results', routing_key='cobra_result.#'),
    Queue('cobra_locals', routing_key='cobra_local.#'),
)
CELERY_TASK_DEFAULT_EXCHANGE = 'tasks'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'task.default'
CELERY_TASK_IGNORE_RESULT = True
# CELERY_TASK_ANNOTATIONS = {
#     'cobra_wrapper.tasks.cobra_fba_save': {
#         'rate_limit': '10/s'
#     },
#     'cobra_wrapper.tasks.cobra_fva_save': {
#         'rate_limit': '10/s'
#     }
# }

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
        },
    },
}

LOGIN_URL = "/"
