#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Create media directory in staticfiles for production
mkdir -p staticfiles/media

# Apply database migrations
python manage.py migrate
