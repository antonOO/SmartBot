"""
Django settings for django_bot project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$l04=-!iu8n521+zrxe9$e!ff8=hz44w=zp3yr6cgs=y7s6#tm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_bot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'django_bot.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

SLACK_CLIENT_ID = "YOUR CLIENT ID"
SLACK_CLIENT_SECRET = "YOUR CLIENT SECRET"

TRAINING_CONFIGURATION_FILE = BASE_DIR + "/config_spacy.json"
TRAINING_MODEL_QUESTION_ORIENTED = BASE_DIR + "/model_20180121-163528"

MIDDLEWARE_URL_ANSWER = "http://sobotmid.pythonanywhere.com/answer"#" "http://localhost:8001/answer/"
MIDDLEWARE_URL_UPDATE_TRAINING_DATA_POSITIVE = "http://sobotmid.pythonanywhere.com/update_training_data_positive/?" #"http://localhost:8001/update_training_data_positive/?"
MIDDLEWARE_URL_UPDATE_TRAINING_DATA_NEGATIVE = "http://sobotmid.pythonanywhere.com/update_training_data_negative/?" #"http://localhost:8001/update_training_data_negative/?"

# MIDDLEWARE_URL_ANSWER = "http://localhost:8001/answer/"
# MIDDLEWARE_URL_UPDATE_TRAINING_DATA_POSITIVE = "http://localhost:8001/update_training_data_positive/?"
# MIDDLEWARE_URL_UPDATE_TRAINING_DATA_NEGATIVE = "http://localhost:8001/update_training_data_negative/?"

INFORMATIVE_MESSAGE = """
                         SOBOT is a helper programming bot, which detects programming questions
                         and tries to find answers on StackOverflow.
                         SOBOT takes a number of commands:

                         @Sobot answers <int>      <--- the answers command takes an integer indicating the number of answers to be output
                         @Sobot toggle             <--- toggles(sets and disables) the autodetection of programming questions
                         @Sobot divergency         <--- toggles(sets and disables) the divergent answer retrieval flag
                                                        (used to return answers from different questions, rather than all the answers
                                                        from the most relevat question)
                         @Sobot <string>           <--- takes a string which is a question to be forwarded to SO
                         @Sobot directsearch       <--- triggers a direct search option (rather than custom ranking on the middleware) -
                                                        the StackOverflow default similarity search
                         """
MINIMAL_NUMBER_OF_WORDS = 4
BOT_UID = 'YOUR BOT ID'
