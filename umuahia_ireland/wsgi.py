"""
WSGI config for umuahia_ireland project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umuahia_ireland.settings")

application = get_wsgi_application()

# Wrap with WhiteNoise for serving static and media files in production
from django.conf import settings

if not settings.DEBUG:
    try:
        from .whitenoise_media import MediaWhiteNoise

        application = MediaWhiteNoise(application)
        print("✅ Using custom WhiteNoise with media file support")
    except ImportError:
        from whitenoise import WhiteNoise

        application = WhiteNoise(application)
        # Manually add media files
        if hasattr(settings, "MEDIA_ROOT") and os.path.exists(settings.MEDIA_ROOT):
            application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
        print("✅ Using standard WhiteNoise with media files")
    except Exception as e:
        print(f"⚠️ WhiteNoise configuration error: {e}")
