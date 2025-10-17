import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

DEFAULT_EMAIL = os.getenv("DEFAULT_EMAIL")

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

APP_NAME = os.getenv("APP_NAME")
APP_URL = os.getenv("APP_URL")
Admin_Email = os.getenv("Admin_Email")

SUPERUSER_EMAIL = os.getenv("SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD")

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

# Stripe Configuration (replacing PayPal)
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Cloudinary Configuration (hardcoded)
# Replace these with your actual Cloudinary credentials
CLOUDINARY_CLOUD_NAME = "your_cloud_name_here"
CLOUDINARY_API_KEY = "your_api_key_here"
CLOUDINARY_API_SECRET = "your_api_secret_here"
