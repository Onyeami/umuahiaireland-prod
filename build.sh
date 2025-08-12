#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create media directories
mkdir -p media/blog/featured
mkdir -p media/blog/images
mkdir -p staticfiles/media/blog/featured
mkdir -p staticfiles/media/blog/images

# Collect static files
python manage.py collectstatic --no-input

# Copy any existing media files to staticfiles
if [ -d "media" ]; then
    cp -r media/* staticfiles/media/ 2>/dev/null || echo "No media files to copy"
fi

# Apply database migrations
python manage.py migrate
