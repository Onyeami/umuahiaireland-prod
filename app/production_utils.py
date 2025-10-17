"""
Production file upload utilities for Render deployment
"""

import os
import shutil
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


def save_uploaded_file_for_production(uploaded_file, upload_path):
    """
    Save uploaded file in both media and staticfiles directories for production
    
    Args:
        uploaded_file: The uploaded file object
        upload_path: The path where the file should be saved (e.g., 'gallery/images/')
    
    Returns:
        The file path relative to MEDIA_URL
    """
    try:
        # Save to regular media directory first
        file_path = default_storage.save(upload_path, ContentFile(uploaded_file.read()))
        
        # In production, also save to staticfiles for serving
        if not settings.DEBUG:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Define staticfiles path
            staticfiles_media_path = os.path.join(
                settings.BASE_DIR, "staticfiles", "media", file_path
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(staticfiles_media_path), exist_ok=True)
            
            # Copy file to staticfiles
            with open(staticfiles_media_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            print(f"✅ File saved to both media/ and staticfiles/media/: {file_path}")
        
        return file_path
        
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        # Fallback to default storage only
        uploaded_file.seek(0)
        return default_storage.save(upload_path, ContentFile(uploaded_file.read()))


def sync_single_file_to_staticfiles(file_path):
    """
    Sync a single media file to staticfiles directory
    
    Args:
        file_path: Path relative to MEDIA_ROOT
    """
    try:
        source_path = os.path.join(settings.MEDIA_ROOT, file_path)
        dest_path = os.path.join(settings.BASE_DIR, "staticfiles", "media", file_path)
        
        if os.path.exists(source_path):
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            print(f"✅ Synced file to staticfiles: {file_path}")
            
    except Exception as e:
        print(f"❌ Error syncing file {file_path}: {e}")