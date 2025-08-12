#!/usr/bin/env python
"""
Simple script to test Cloudinary configuration
Run this after setting up Cloudinary environment variables
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "umuahia_ireland.settings")
django.setup()

from django.conf import settings


def test_cloudinary_config():
    print("🔍 Testing Cloudinary Configuration...\n")

    # Check if we're in production mode
    print(f"DEBUG: {settings.DEBUG}")

    if settings.DEBUG:
        print("📍 Running in DEVELOPMENT mode")
        print(f"   MEDIA_URL: {settings.MEDIA_URL}")
        print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
        return

    print("📍 Running in PRODUCTION mode")

    # Check environment variables
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    print("\n🔑 Environment Variables:")
    print(f"   CLOUDINARY_CLOUD_NAME: {'✅ Set' if cloud_name else '❌ Missing'}")
    print(f"   CLOUDINARY_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"   CLOUDINARY_API_SECRET: {'✅ Set' if api_secret else '❌ Missing'}")

    # Check Django settings
    print(f"\n⚙️  Django Settings:")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")

    if hasattr(settings, "DEFAULT_FILE_STORAGE"):
        print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")

    # Test Cloudinary import
    try:
        import cloudinary
        import cloudinary.uploader

        print(f"\n📦 Cloudinary packages: ✅ Installed")

        if all([cloud_name, api_key, api_secret]):
            print(f"🎯 Cloudinary Status: ✅ CONFIGURED")
            print(f"   Cloud Name: {cloud_name}")
            print(
                f"   Media will be stored at: https://res.cloudinary.com/{cloud_name}/"
            )
        else:
            print(f"🎯 Cloudinary Status: ❌ NOT CONFIGURED")
            print("   Missing environment variables")

    except ImportError as e:
        print(f"\n📦 Cloudinary packages: ❌ Not installed")
        print(f"   Error: {e}")

    print("\n" + "=" * 50)

    if all([cloud_name, api_key, api_secret]):
        print("🎉 READY! Blog images should work in production")
    else:
        print("⚠️  ACTION NEEDED:")
        print("   1. Set up Cloudinary account at cloudinary.com")
        print("   2. Add environment variables in Render dashboard")
        print("   3. Redeploy your application")


if __name__ == "__main__":
    test_cloudinary_config()
