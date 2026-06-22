from pathlib import Path
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-jj9=2^^sdz8p8!3aseru4kij-$zas$q4&j_)@dk_-pqr%6rlv^'

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
    "django.contrib.humanize",

    #3rd party
    "phonenumber_field",
    "django_filters",

    #local
    'landing',
    'accounts',
    'cart',
    'order',
    "product.apps.ProductConfig",
    'core',
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

ROOT_URLCONF = 'new_danidor.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "cart.context_processors.cart_counter",
            ],
        },
    },
]

WSGI_APPLICATION = 'new_danidor.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "statics",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = 'accounts.User'

PHONENUMBER_DEFAULT_REGION = "IR"
PHONENUMBER_DB_FORMAT = "E164"  # store as +98...
LOCALE_PATHS = [BASE_DIR / "locale"]
LANGUAGES = [("fa", "Farsi"), ("en", "English")]


CHECKOUT_SESSION_TTL_MINUTES = 60
CHECKOUT_TAX_PERCENT = 10
CHECKOUT_SHIPPING_PRICE_TOMAN = 0


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}






CELERY_BROKER_URL = "redis://localhost:6379/0"

# Optional, but useful
CELERY_TIMEZONE = "Asia/Tehran"  # or your project timezone
CELERY_ENABLE_UTC = True

# You do not need a result backend for this cleanup task.
CELERY_RESULT_BACKEND = None

CELERY_TASK_IGNORE_RESULT = True

CELERY_BEAT_SCHEDULE = {
    "abandon-old-active-carts-every-night": {
        "task": "cart.tasks.abandon_old_active_carts",
        "schedule": crontab(hour=3, minute=0),
        "kwargs": {
            "days": 7,
        },
    },
    "delete-old-abandoned-carts-every-night": {
        "task": "cart.tasks.delete_old_abandoned_carts",
        "schedule": crontab(hour=4, minute=0),
        "kwargs": {
            "days": 30,
        },
    },
}