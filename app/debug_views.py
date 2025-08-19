from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
import os


@staff_member_required
def debug_cloudinary_config(request):
    """Debug view to check Cloudinary configuration (admin only)"""
    return JsonResponse(
        {
            "cloudinary_cloud_name": bool(os.getenv("CLOUDINARY_CLOUD_NAME")),
            "cloudinary_api_key": bool(os.getenv("CLOUDINARY_API_KEY")),
            "cloudinary_api_secret": bool(os.getenv("CLOUDINARY_API_SECRET")),
            "cloud_name_length": len(os.getenv("CLOUDINARY_CLOUD_NAME", "")),
            "api_key_length": len(os.getenv("CLOUDINARY_API_KEY", "")),
            "api_secret_length": len(os.getenv("CLOUDINARY_API_SECRET", "")),
        }
    )
