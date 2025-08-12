"""
Custom WhiteNoise configuration to serve media files in production
"""

from whitenoise import WhiteNoise
from django.conf import settings
import os


class MediaWhiteNoise(WhiteNoise):
    """
    Extends WhiteNoise to serve media files in production
    """

    def __init__(self, application, **kwargs):
        super().__init__(application, **kwargs)

        # Add media files to WhiteNoise if not using Cloudinary
        if not settings.DEBUG and hasattr(settings, "MEDIA_ROOT"):
            media_root = settings.MEDIA_ROOT
            if os.path.exists(media_root):
                self.add_files(media_root, prefix=settings.MEDIA_URL)
                print(f"✅ WhiteNoise serving media files from: {media_root}")
