"""
Django settings for pips_shop project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import sys

from pathlib import Path
import environ


root = environ.Path(__file__) - 2  # two folders back (/a/b/ - 3 = /)

# defaults
env = environ.Env(
    DEBUG=(bool, False),
    SHOW_DEBUG_TOOLBAR=(bool, False),
    USE_MAILCATCHER=(bool, False),
    LOCAL=(bool, False),
    TESTING=(bool, False),
    CI=(bool, False),
)

environ.Env.read_env(root("pips_shop/.env"))  # reading .env file

TESTING = env("TESTING")
if not TESTING:  # pragma: no cover
    TESTING = any(
        [test_str in arg for arg in sys.argv for test_str in ["test", "pytest"]]
    )

BASE_DIR = root()
PROJECT_DIR = root("pips_shop")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")
if SECRET_KEY is None:  # pragma: no cover
    print("No secret key!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
# when env variable is changed it will be a string, not bool
if str(DEBUG).lower() in ["true", "on"]:  # pragma: no cover
    DEBUG = True
else:  # pragma: no cover
    DEBUG = False


DOMAIN = env.str("DOMAIN")
ALLOWED_HOSTS = [
    DOMAIN, 
    f'www.{DOMAIN}', 
    f"vagrant.{DOMAIN}",
    f"www.vagrant.{DOMAIN}",
]
# https://docs.djangoproject.com/en/4.0/ref/settings/#std:setting-CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    f'https://{DOMAIN}', 
    f'https://*.{DOMAIN}', 
    f'https://vagrant.{DOMAIN}',
    f'https://*.vagrant.{DOMAIN}',
]



if env("LOCAL"):  # pragma: no cover
    ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "home",
    "dashboard",
    "search",
    "django_extensions",
    "django_ses",
    "wagtail.contrib.forms",
    "wagtail.contrib.frontend_cache",
    "wagtail.contrib.modeladmin",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap4",
    "salesman.core",
    "salesman.basket",
    "salesman.checkout",
    "salesman.orders",
    "salesman.admin",
    "rest_framework",
    "shop",
    "salesman_stripe",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "pips_shop.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "shop.context_processors.shop_context",
            ],
        },
    },
]

WSGI_APPLICATION = "pips_shop.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": env.db(),
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
}


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


if TESTING or env('LOCAL') or env('CI'):  # use local cache for tests
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-pins',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
            'LOCATION': '127.0.0.1:11211',
            'KEY_PREFIX': 'pins',
        }
    }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

STATIC_ROOT = os.path.join(BASE_DIR, "collected-static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Email
if env("LOCAL") or env("CI") or env("TESTING"):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:  # pragma: no cover
    EMAIL_BACKEND = "django_ses.SESBackend"
    AWS_SES_ACCESS_KEY_ID = env("AWS_SES_ACCESS_KEY_ID")
    AWS_SES_SECRET_ACCESS_KEY = env("AWS_SES_SECRET_ACCESS_KEY")
    AWS_SES_REGION_NAME = env("AWS_SES_REGION_NAME")
    AWS_SES_REGION_ENDPOINT = env("AWS_SES_REGION_ENDPOINT")

DEFAULT_FROM_EMAIL = "watermelon.bookings+no-reply@gmail.com"
SUPPORT_EMAIL = "rebkwok@gmail.com"
SERVER_EMAIL = SUPPORT_EMAIL

# MAILCATCHER
if env("USE_MAILCATCHER"):  # pragma: no cover
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "127.0.0.1"
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False


# #####LOGGING######
if not TESTING and not env("LOCAL"):  # pragma: no cover
    LOG_FOLDER = env("LOG_FOLDER")

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "[%(levelname)s] - %(asctime)s - %(name)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "file_app": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_FOLDER, "pins.log"),
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "verbose",
            },
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "mail_admins": {
                "level": "ERROR",
                "class": "django.utils.log.AdminEmailHandler",
                "include_html": True,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file_app", "mail_admins"],
                "propagate": True,
            },
            "django.request": {
                "handlers": ["console", "file_app", "mail_admins"],
                "propagate": True,
            },
            "home": {
                "handlers": ["console", "file_app", "mail_admins"],
                "level": "INFO",
                "propagate": False,
            },
            "search": {
                "handlers": ["console", "file_app", "mail_admins"],
                "level": "INFO",
                "propagate": False,
            },
            "shop": {
                "handlers": ["console", "file_app", "mail_admins"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
else:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
            }
        },
        "loggers": {
            "django.request": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": True,
            },
            "home": {
                "handlers": ["console"],
                "level": "INFO",
                "propogate": True,
            },
            "search": {
                "handlers": ["console"],
                "level": "INFO",
                "propogate": True,
            },
            "shop": {
                "handlers": ["console"],
                "level": "INFO",
                "propogate": True,
            },
        },
    }

ADMINS = [("Becky Smith", SUPPORT_EMAIL)]

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INTERNAL_IPS = ("127.0.0.1", "10.0.2.2")


# Session cookies
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 604800  # 1 week

if env("LOCAL") or TESTING:
    SESSION_COOKIE_SECURE = False
else:  # pragma: no cover
    SESSION_COOKIE_SECURE = True


# Wagtail settings

WAGTAIL_SITE_NAME = "The Watermelon Studio Shop"

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
WAGTAILADMIN_BASE_URL = f'https://{DOMAIN}'


WAGTAILIMAGES_JPEG_QUALITY = 65
WAGTAILIMAGES_WEBP_QUALITY = 65

# Salesman

SALESMAN_ADMIN_REGISTER = False
SALESMAN_BASKET_MODEL = "shop.Basket"
SALESMAN_BASKET_ITEM_MODEL = "shop.BasketItem"
SALESMAN_ORDER_MODEL = "shop.Order"
SALESMAN_ORDER_ITEM_MODEL = "shop.OrderItem"
SALESMAN_ORDER_PAYMENT_MODEL = "shop.OrderPayment"
SALESMAN_ORDER_NOTE_MODEL = "shop.OrderNote"
SALESMAN_ORDER_SERIALIZER = "shop.serializers.OrderSerializer"

SALESMAN_PRODUCT_TYPES = {
    "shop.ProductVariant": "shop.serializers.ProductVariantSerializer",
}
SALESMAN_PAYMENT_METHODS = [
    # "shop.payment.PayInAdvance",
    "shop.payment.PayByStripe",
]
SALESMAN_BASKET_MODIFIERS = [
    "shop.modifiers.ShippingCostModifier",
]

# for crispy forms
CRISPY_TEMPLATE_PACK = "bootstrap4"
USE_CRISPY = True

SALESMAN_STRIPE_SECRET_KEY=env.str("SALESMAN_STRIPE_SECRET_KEY")
SALESMAN_STRIPE_WEBHOOK_SECRET=env.str("SALESMAN_STRIPE_WEBHOOK_SECRET")

# Account ID for Stripe connect account
STRIPE_CONNECTED_ACCOUNT=env.str("STRIPE_CONNECTED_ACCOUNT")

# Payment method label used when displayed in the basket.
SALESMAN_STRIPE_PAYMENT_LABEL = 'Pay with Stripe'

# Default ISO currency used for payments (https://stripe.com/docs/currencies)
SALESMAN_STRIPE_DEFAULT_CURRENCY = 'gbp'

SALESMAN_STRIPE_WEBHOOK_URL = "/stripe/webhook/"
# Default paid status for fullfiled orders.
# SALESMAN_STRIPE_PAID_STATUS = 'PROCESSING'
