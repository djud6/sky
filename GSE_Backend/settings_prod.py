"""
Django settings for GSE_Backend project.
"""

import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CERT_PATH = os.path.join(BASE_DIR, 'GSE_Backend', 'SSL', 'DigiCertGlobalRootG2.crt.pem') 

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']
REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_api_key',
    'api',
    'core',
    'analytics',
    'api_vendor',
    'communication',
    'api_auth',
    'corsheaders'
]
AUTH_USER_MODEL = 'api_auth.User'
MIDDLEWARE = [
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.db_router.RouterMiddleware.RouterMiddleware',
    ]

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')

ADMINS = [('Ana Z', 'azakharova@skyit.services'), ('Slavi Paskalev', 'sppaskal@skyit.com'),
          ('Admin account', 'errors@skyit.services'), ('Anshul Dubey', 'adubey@skyit.com')]

MANAGERS = ADMINS

SUPPORT_EMAIL = "aukai-support@skyit.services"
ARCHIVE_EMAIL = "aukai-archive@skyit.services"

CORS_ORIGIN_ALLOW_ALL = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters':{
        'standard':{
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(SITE_ROOT, 'logs/logs.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter': 'standard'
        },

        'request_handler' :{
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(SITE_ROOT, 'logs/django-requests.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_handler', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

ROOT_URLCONF = 'GSE_Backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'GSE_Backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASE_ROUTERS = ['api.db_router.AuthRouter.AuthRouter',
                    'api.db_router.OtherRouter.OtherRouter']
DATABASES = {
    'default': {},
    'auth_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skyit_auth',
        'USER': os.getenv('DB_USERNAME'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '3306',
        'OPTIONS': {'ssl': {'ca': CERT_PATH}},
    },
    'wj': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skyit_gse',
        'USER': os.getenv('DB_USERNAME'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '3306',
        'OPTIONS': {'ssl': {'ca': CERT_PATH}},
    },
    'fmt': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skyit_fmt',
        'USER': os.getenv('DB_USERNAME'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '3306',
        'OPTIONS': {'ssl': {'ca': CERT_PATH}},
    },
    'fmt_test': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skyit_fmt_test',
        'USER': os.getenv('DB_USERNAME'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '3306',
        'OPTIONS': {'ssl': {'ca': CERT_PATH}},
    },
}

# Number of seconds before token expires - 1year = 31622400
TOKEN_EXPIRED_AFTER_SECONDS = 31622400

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

# Django email services
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

CONNECTION_STRINGS = {
    "WestJet": os.getenv('WJ_CONNECTION_STRING'),
    "FMT": os.getenv('FMT_CONNECTION_STRING')
}


sentry_sdk.init(
    dsn="https://137a7ed6035a4910b4a5a1eda8300d78@o587099.ingest.sentry.io/5738507",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)