from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import os


@staff_member_required
def media_test_view(request):
    """
    Quick test view to debug media file issues
    """
    debug_info = {
        "DEBUG": settings.DEBUG,
        "MEDIA_URL": settings.MEDIA_URL,
        "MEDIA_ROOT": str(settings.MEDIA_ROOT),
        "media_root_exists": (
            os.path.exists(settings.MEDIA_ROOT)
            if hasattr(settings, "MEDIA_ROOT")
            else False
        ),
    }

    # Check for cloudinary configuration
    cloudinary_env_vars = {
        "CLOUDINARY_CLOUD_NAME": bool(os.getenv("CLOUDINARY_CLOUD_NAME")),
        "CLOUDINARY_API_KEY": bool(os.getenv("CLOUDINARY_API_KEY")),
        "CLOUDINARY_API_SECRET": bool(os.getenv("CLOUDINARY_API_SECRET")),
    }

    # Check storage backend
    storage_backend = getattr(settings, "DEFAULT_FILE_STORAGE", "default")

    # List media files if directory exists
    media_files = []
    if hasattr(settings, "MEDIA_ROOT") and os.path.exists(settings.MEDIA_ROOT):
        try:
            for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                for file in files:
                    rel_path = os.path.relpath(
                        os.path.join(root, file), settings.MEDIA_ROOT
                    )
                    media_files.append(rel_path)
        except Exception as e:
            media_files = [f"Error listing files: {str(e)}"]

    return JsonResponse(
        {
            "django_settings": debug_info,
            "cloudinary_env_vars": cloudinary_env_vars,
            "storage_backend": storage_backend,
            "media_files": media_files[:10],  # First 10 files
            "status": "success",
        }
    )
