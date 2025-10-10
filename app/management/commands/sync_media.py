"""
Management command to sync media files to staticfiles directory for production serving
"""

import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Sync media files to staticfiles directory for production serving'

    def handle(self, *args, **options):
        # Define source and destination paths
        source_media = os.path.join(settings.BASE_DIR, "media")
        dest_media = os.path.join(settings.BASE_DIR, "staticfiles", "media")

        self.stdout.write("Starting media file synchronization...")

        try:
            # Create destination directory if it doesn't exist
            os.makedirs(dest_media, exist_ok=True)

            # Check if source media directory exists and has content
            if os.path.exists(source_media) and os.listdir(source_media):
                # Remove existing destination to ensure clean copy
                if os.path.exists(dest_media):
                    shutil.rmtree(dest_media)
                
                # Copy media files
                shutil.copytree(source_media, dest_media)
                
                # Count copied files
                file_count = 0
                for root, dirs, files in os.walk(dest_media):
                    file_count += len(files)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Successfully copied {file_count} media files from {source_media} to {dest_media}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING("⚠️ No media files found to copy")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error syncing media files: {e}")
            )