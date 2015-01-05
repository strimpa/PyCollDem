"""
Django settings for PyCollDem project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '29ykgydlrxx=x6g3^u%^rvg)gmf*m3x1vi9vv87z#c$l91r1&t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

AUTH_USER_MODEL = 'CollDem.CollDemUser'

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = (
	os.path.join(BASE_DIR, 'CollDem', 'templates'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_facebook',
    'oauth_tokens',
    'm2m_history',
    'taggit',
    'twitter_api',
    'CollDem'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'django_facebook.context_processors.facebook',
)

AUTHENTICATION_BACKENDS = (
    'django_facebook.auth_backends.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'PyCollDem.urls'

WSGI_APPLICATION = 'PyCollDem.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

print BASE_DIR + '/PyCollDem/mariadb.cnf'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
	'OPTIONS': {
            'read_default_file': BASE_DIR + '/PyCollDem/mariadb.cnf',
        },
#	'USER' : 'django_user'
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'GMT'

USE_I18N = True

USE_L10N = True

USE_TZ = True

EMAIL_HOST = 'mail.tuets.com'

EMAIL_PORT = 587

EMAIL_HOST_USER = 'mail@tuets.com'

EMAIL_HOST_PASSWORD = 'ernieundbert'

EMAIL_USE_TLS = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'


#############################################################################
# plugins

# facebook 

FACEBOOK_APP_ID = "757643464272609"

FACEBOOK_APP_SECRET = "6f5ba4aaae6b7cb38ea92371a36d5db4"

#twitter app

# oauth-tokens settings
OAUTH_TOKENS_HISTORY = True                                        # to keep in DB expired access tokens
OAUTH_TOKENS_TWITTER_CLIENT_ID = 'pitchf.org'                                # application ID
OAUTH_TOKENS_TWITTER_CLIENT_SECRET = 'Du5ZToHr9KQ842gecHP6NKSp4PwTNzubvva0MPa2CGNd30tZtT'                            # application secret key
OAUTH_TOKENS_TWITTER_USERNAME = 'gunchirp'                                 # user login
OAUTH_TOKENS_TWITTER_PASSWORD = 'UnsOnsay1'                                 # user password