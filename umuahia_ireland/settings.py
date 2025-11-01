import os
import dj_database_url
from pathlib import Path
from .config import (
    SECRET_KEY,
    DEBUG,
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
    PAYPAL_CLIENT_ID,
    STRIPE_PUBLISHABLE_KEY,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
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
    "cloudinary_storage",
    "cloudinary",
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
    "umuahia_ireland.middleware.CSRFDebugMiddleware",  # Debug CSRF issues
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
                "umuahia_ireland.context_processors.stripe_settings",
                "umuahia_ireland.title_context_processor.dynamic_page_title",
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
            "postgresql://umuahiaireland_db_user:gGuHDNCpqqDUqfiR1Xk9YtwdckJ8VQWB@dpg-d3ml1hbuibrs738vkqo0-a.oregon-postgres.render.com/umuahiaireland_db",
        ),
        conn_max_age=600,
        ssl_require=True,  # Render requires SSL for connections
    )
}

# Session Configuration
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF Configuration
CSRF_COOKIE_AGE = 3600  # 1 hour
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = False  # Must be False so JavaScript can read it
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_USE_SESSIONS = False  # Keep tokens in cookies, not sessions
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://*.render.com",
]

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

    # Add media files to WhiteNoise configuration
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_AUTOREFRESH = True


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Production media file handling
if not DEBUG:
    # First, try Cloudinary if configured
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api

        # Cloudinary settings - using hardcoded credentials from config
        CLOUDINARY_STORAGE = {
            "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
            "API_KEY": CLOUDINARY_API_KEY,
            "API_SECRET": CLOUDINARY_API_SECRET,
        }

        # Only use cloudinary in production if credentials are available
        if all(CLOUDINARY_STORAGE.values()):
            cloudinary.config(
                cloud_name=CLOUDINARY_STORAGE["CLOUD_NAME"],
                api_key=CLOUDINARY_STORAGE["API_KEY"],
                api_secret=CLOUDINARY_STORAGE["API_SECRET"],
                secure=True,
            )

            # Use Cloudinary for media storage
            DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
            MEDIA_URL = (
                f'https://res.cloudinary.com/{CLOUDINARY_STORAGE["CLOUD_NAME"]}/'
            )
            print(
                f"✅ Cloudinary configured for cloud: {CLOUDINARY_STORAGE['CLOUD_NAME']}"
            )
        else:
            # Fallback: Use WhiteNoise to serve media files
            # Store media files alongside static files for persistence
            MEDIA_ROOT = os.path.join(BASE_DIR, "staticfiles", "media")
            MEDIA_URL = "/media/"

            # Enable WhiteNoise to serve media files
            WHITENOISE_USE_FINDERS = True
            WHITENOISE_AUTOREFRESH = True
            WHITENOISE_MAX_AGE = 31536000  # 1 year cache for media files

            print("⚠️  Cloudinary not configured - using WhiteNoise for media files")
            print(f"   Media files will be served from: {MEDIA_ROOT}")
            print(
                "   Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET"
            )
    except ImportError:
        # Fallback if cloudinary packages not installed
        MEDIA_ROOT = os.path.join(BASE_DIR, "staticfiles", "media")
        MEDIA_URL = "/media/"

        # Enable WhiteNoise to serve media files
        WHITENOISE_USE_FINDERS = True
        WHITENOISE_AUTOREFRESH = True
        WHITENOISE_MAX_AGE = 31536000

        print("⚠️  Cloudinary packages not installed - using WhiteNoise for media files")
        print(f"   Media files will be served from: {MEDIA_ROOT}")

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

# PayPal Configuration (Legacy - can be removed)
PAYPAL_CLIENT_ID = PAYPAL_CLIENT_ID

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY = STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET = STRIPE_WEBHOOK_SECRET
