from django import forms
from .models import Minuites, FinancialCheckbook
import cloudinary
import cloudinary.uploader
from django.conf import settings
import os


def upload_to_cloudinary(file):
    """Upload file to Cloudinary and return the URL"""
    try:
        # Get Cloudinary credentials
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "")
        api_key = os.getenv("CLOUDINARY_API_KEY", "")
        api_secret = os.getenv("CLOUDINARY_API_SECRET", "")

        # Debug logging for deployment
        print(f"Cloudinary Config - Cloud Name: {'***' if cloud_name else 'MISSING'}")
        print(f"Cloudinary Config - API Key: {'***' if api_key else 'MISSING'}")
        print(f"Cloudinary Config - API Secret: {'***' if api_secret else 'MISSING'}")

        if not all([cloud_name, api_key, api_secret]):
            print("ERROR: Missing Cloudinary credentials!")
            return None

        # Configure Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        # Determine resource type based on file extension
        file_name = getattr(file, "name", "")
        if file_name.lower().endswith((".pdf", ".doc", ".docx", ".txt")):
            resource_type = "raw"
        else:
            resource_type = "auto"

        print(f"Uploading file: {file_name} as {resource_type}")

        # Upload the file
        result = cloudinary.uploader.upload(
            file,
            folder="documents",  # Upload to documents folder in Cloudinary
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
        )

        cloudinary_url = result["secure_url"]
        print(f"Upload successful! URL: {cloudinary_url}")
        return cloudinary_url

    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        import traceback

        print(f"Full traceback: {traceback.format_exc()}")
        return None


class MinuitesForm(forms.ModelForm):
    class Meta:
        model = Minuites
        fields = ["title", "date", "minuites"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "minuites": forms.FileInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If a new file is uploaded, try to upload to Cloudinary
        if self.files.get("minuites"):
            uploaded_file = self.files["minuites"]
            cloudinary_url = upload_to_cloudinary(uploaded_file)
            if cloudinary_url:
                instance.minuites_url = cloudinary_url
                print(f"Minutes file uploaded to Cloudinary: {cloudinary_url}")
            else:
                print("Failed to upload to Cloudinary, file will be saved locally")
                # File will still be saved to the FileField normally

        if commit:
            instance.save()
        return instance


class FinancialCheckbookForm(forms.ModelForm):
    class Meta:
        model = FinancialCheckbook
        fields = ["title", "date", "checkbook"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "checkbook": forms.FileInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If a new file is uploaded, try to upload to Cloudinary
        if self.files.get("checkbook"):
            uploaded_file = self.files["checkbook"]
            cloudinary_url = upload_to_cloudinary(uploaded_file)
            if cloudinary_url:
                instance.checkbook_url = cloudinary_url
                print(f"Checkbook file uploaded to Cloudinary: {cloudinary_url}")
            else:
                print("Failed to upload to Cloudinary, file will be saved locally")
                # File will still be saved to the FileField normally

        if commit:
            instance.save()
        return instance
