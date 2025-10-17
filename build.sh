#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Create comprehensive media directory structure
echo "Creating media directories..."
mkdir -p media/blog/featured
mkdir -p media/blog/images
mkdir -p media/gallery/images
mkdir -p media/gallery/videos
mkdir -p media/gallery/covers
mkdir -p media/gallery/thumbnails
mkdir -p media/minuites
mkdir -p media/checkbooks
mkdir -p media/testimonials

# Create corresponding staticfiles directories
echo "Creating staticfiles media directories..."
mkdir -p staticfiles/media/blog/featured
mkdir -p staticfiles/media/blog/images
mkdir -p staticfiles/media/gallery/images
mkdir -p staticfiles/media/gallery/videos
mkdir -p staticfiles/media/gallery/covers
mkdir -p staticfiles/media/gallery/thumbnails
mkdir -p staticfiles/media/minuites
mkdir -p staticfiles/media/checkbooks
mkdir -p staticfiles/media/testimonials

# Apply database migrations first
echo "Applying database migrations..."
python manage.py migrate --no-input

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Sync media files to staticfiles for serving
echo "Syncing media files to staticfiles..."
python manage.py sync_media

echo "Build completed successfully!"
