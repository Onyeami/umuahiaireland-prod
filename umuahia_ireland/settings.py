import os
import dj_database_url
from pathlib import Path
from .config import (
    SECRET_KEY,
    DEBUG,
    ALLOWED_HOSTS,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD,
    APP_NAME,
    APP_URL,
    Admin_Email,
    SUPERUSER_EMAIL,
    SUPERUSER_PASSWORD,
)

APP_NAME = APP_NAME
APP_URL = APP_URL
Admin_Email = Admin_Email

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = SECRET_KEY

DEBUG = DEBUG

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Third party apps
    "django_extensions",
    # Local apps
    "app.apps.AppConfig",
    "_admin.apps.AdminConfig",
    "dashboard.apps.DashboardConfig",
    "users.apps.UsersConfig",
    "blog.apps.BlogConfig",
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
]

ROOT_URLCONF = "umuahia_ireland.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "_admin.context_processors.global_counts",
                "umuahia_ireland.context_processors.paypal_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "umuahia_ireland.wsgi.application"

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": DB_NAME,
#         "USER": DB_USER,
#         "PASSWORD": DB_PASSWORD,
#         "HOST": DB_HOST,
#         "PORT": DB_PORT,
#     }
# }

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",
            "postgresql://umuahia_db_cjtb_user:tnVzOQdGLPMsXXleQsTQVdCTdy6IzsWY@dpg-cvtq0lbe5dus73ad9ltg-a.oregon-postgres.render.com/umuahia_db_cjtb",
        ),
        conn_max_age=600,
        ssl_require=True,  # Render requires SSL for connections
    )
}


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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "accounts:login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_EMAIL = EMAIL_HOST_USER

AUTH_USER_MODEL = "users.CustomUser"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD


SUPERUSER_EMAIL = (SUPERUSER_EMAIL,)
SUPERUSER_PASSWORD = (SUPERUSER_PASSWORD,)

# # Security Settings for Production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_TZ = True
    X_FRAME_OPTIONS = "DENY"

    # Update ALLOWED_HOSTS for production
    ALLOWED_HOSTS = [
        "localhost",
        "127.0.0.1",
        "*.herokuapp.com",
        "*.render.com",
    ]
