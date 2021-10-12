import os
from django.urls import reverse_lazy
from django.contrib.messages import constants as messages
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CONFIGURACIÓN PARA EL ENVIO AUTOMÁTICO DE CORREOS:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'danielcorderomeza2021@gmail.com'  # CORREO DEL SITIO WEB
# EMAIL_HOST_PASSWORD = '$$Clave1234'
# EMAIL_PORT = 587

# PARA QUE FUNCIONE EN PYTHONANYWHERE:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_SERVER = 'smtp.gmail.com'
EMAIL_HOST_USER = 'danielcorderomeza2021@gmail.com'  # CORREO DEL SITIO WEB
EMAIL_HOST_PASSWORD = '$$Clave1234'
EMAIL_PORT = 465

# MAIL_SERVER = "smtp.gmail.com"
# MAIL_USERNAME = "danielcorderomeza2021@gmail.com"
# MAIL_PASSWORD = "$$Clave1234"
# MAIL_PORT = 465
# MAIL_USE_SSL = True
# MAIL_USE_TLS = False

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2&5+#3u5u)pyb1yq3=g^)#l03s*u^e$@q*87nq@s(1(3de6agl'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # False para fase de producción

if DEBUG is True:
    ALLOWED_HOSTS = [
        'dero86.pythonanywhere.com',
        '*'
    ]
else:
    ALLOWED_HOSTS = [
    'dero86.pythonanywhere.com',
    '*',
    ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ProyectoApp',  # Nombre de la aplicación web
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

ROOT_URLCONF = 'Proyecto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '\\ProyectoApp\\templates\\ProyectoApp')],
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

WSGI_APPLICATION = 'Proyecto.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'd8mhv679bmtfem',
        'USER': 'sashfauqymexpt',
        'PASSWORD': '65b0ed1cfe2fa2bd6daff0348998ae42adf40ae3654ab72e030636a61c9ef832',
        'HOST': 'ec2-52-7-228-45.compute-1.amazonaws.com',
        'PORT': '5432',
    }
}"""
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

LANGUAGE_CODE = 'es-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
AUTH_USER_MODEL = 'ProyectoApp.CustomUser'

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}