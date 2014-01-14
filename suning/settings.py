#coding: utf-8
# Django settings for suning project.
import os


from pyhdfs import hdfs

DEBUG = True
#DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('yangchen', 'yuhan534@126.com'),
)

EMPTY_VALUE = '&mdash;'

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '3306'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'nameLR9969'
DATABASE_NAME = 'tianyin'

DATABASES = {
    'default': {
        'ENGINE': 'django_mysqlpool.backends.mysqlpool',#'django.db.backends.mysqlpool', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DATABASE_NAME,                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'HOST': DATABASE_HOST,                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': DATABASE_PORT,                      # Set to empty string for default.
    }
}

HDFS_CONFIG = {
    'username': 'songwei', #HDFS linux owner username
    'hostname': 'localhost', #HDFS web host name
    'port': '50070' #HDFS web port
}

hdfs.setConfig(**HDFS_CONFIG)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

EMAIL_HOST="smtp.qq.com"
EMAIL_HOST_USER="491320274"
EMAIL_HOST_PASSWORD="bachisback1"
FROM_EMAIL = "491320274@qq.com"

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

LANGUAGE_CODE = 'zh_CN'
FILE_CHARSET='UTF-8'
DEFAULT_CHARSET = 'UTF-8'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.normpath(__file__)))
# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '/data/media'
#MEDIA_ROOT = '/home/yangchen/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = PROJECT_ROOT + '/static'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    PROJECT_ROOT + '/assets',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

LOGIN_URL = '/welcome'
PERMISSION_DENIED_URL = '/permission_denied'

LOGIN_JSON_URL = "/welcome_json"
PERMISSION_DENIED_JSON_URL = "/permission_denied_json"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'dajaxice.finders.DajaxiceFinder'
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'm_8#r3b(v4r+g6y-l=!2mvwx!c75nu2y3$6d6flu$hk2q3j%m0'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages")

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'auth_remember.backend.AuthRememberBackend'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'auth_remember.middleware.AuthRememberMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'suning.urls'

PAGINATION_PAGE_SIZE = 10
NO_SEARCH_RESULTS = u'无搜索结果'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'suning.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

CRONJOBS = [
    ('00 00 * * *', 'ad.cron.update_index'),
    ('00 00 * * *', 'framework.cron.clear_expired_token')
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    #'haystack',
    #'djangosphinx'
    'framework',
    'ad',
    'mgr',
    'app',
    'rest_framework',
    'interface',
    'statistics',
    'feedback',
    'django_tables2',
    'ajax_upload',
    'django_select2',
	'dajaxice',
    'django_crontab',
    'parsley',
    'auth_remember',
)

AUTH_REMEMBER_COOKIE_NAME = 'remember_token'
AUTH_REMEMBER_COOKIE_AGE = 86400 * 2

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
        'windows2x': {
            'format': '[windows2x]%(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'django': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_ROOT + '/logs/','django.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        },
        'windows2x': {
            'level':'INFO',
            'class':'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(PROJECT_ROOT + '/logs/','windows2x.log'),
            #'maxBytes': 1024*1024*5,
            'backupCount': 7,
            'formatter':'windows2x',
            'when':'midnight',
        },
        'default': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(PROJECT_ROOT + '/logs/','suning_default.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'windows2x.post': {
            'handlers': ['windows2x'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['django'],
            'level': 'DEBUG',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['default'],
        'level': 'DEBUG',
        'propagate': False,
    }
}


if not DEBUG:
    import django.core.files.storage
    import interface.storage
    storage = interface.storage.hdfs_storage()
    django.core.files.storage.default_storage.listdir = storage.listdir
    django.core.files.storage.default_storage.exist = storage.exist
    django.core.files.storage.default_storage.delete = storage.delete
    #DEFAULT_FILE_STORAGE = 'interface.storage.hdfs_storage'

