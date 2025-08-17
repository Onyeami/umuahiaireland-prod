from django import forms
from .models import Minuites, FinancialCheckbook
import cloudinary
import cloudinary.uploader
from django.conf import settings
import os


def upload_to_cloudinary(file):
    """Upload file to Cloudinary and return the URL"""
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.getenv("CLOUDINARY_API_KEY", ""),
            api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
            secure=True,
        )

        # Determine resource type based on file extension
        file_name = getattr(file, "name", "")
        if file_name.lower().endswith((".pdf", ".doc", ".docx", ".txt")):
            resource_type = "raw"
        else:
            resource_type = "auto"

        # Upload the file
        result = cloudinary.uploader.upload(
            file,
            folder="documents",  # Upload to documents folder in Cloudinary
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
        )

        return result["secure_url"]
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
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

        # If a new file is uploaded, upload to Cloudinary
        if self.files.get("minuites"):
            uploaded_file = self.files["minuites"]
            cloudinary_url = upload_to_cloudinary(uploaded_file)
            if cloudinary_url:
                instance.minuites_url = cloudinary_url

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

        # If a new file is uploaded, upload to Cloudinary
        if self.files.get("checkbook"):
            uploaded_file = self.files["checkbook"]
            cloudinary_url = upload_to_cloudinary(uploaded_file)
            if cloudinary_url:
                instance.checkbook_url = cloudinary_url

        if commit:
            instance.save()
        return instance
