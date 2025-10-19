from django import forms
from django.forms.widgets import ClearableFileInput
from django.utils import timezone
from .models import Minuites, FinancialCheckbook, GalleryFolder, GalleryImage, GalleryVideo, Testimonial, MembersGalleryImage
import cloudinary
import cloudinary.uploader
from django.conf import settings
import os
import json


class AlertEnabledFileInput(ClearableFileInput):
    """Custom file input widget with alert system integration"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control file-upload-input',
            'data-upload-alerts': 'true'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    class Media:
        css = {
            'all': ('css/file-upload-alerts.css',)
        }
        js = ('js/file-upload-alerts.js',)


class AlertEnabledFormMixin:
    """Mixin to add alert functionality to forms"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add alert data attributes to the form
        if hasattr(self, 'Meta') and hasattr(self.Meta, 'widgets'):
            for field_name, widget in self.Meta.widgets.items():
                if isinstance(widget, forms.FileInput):
                    # Replace with alert-enabled widget
                    self.fields[field_name].widget = AlertEnabledFileInput(attrs=widget.attrs)
    
    def add_upload_result(self, field_name, success, message, cloudinary_url=None):
        """Add upload result data for JavaScript alerts"""
        if not hasattr(self, '_upload_results'):
            self._upload_results = {}
        
        self._upload_results[field_name] = {
            'success': success,
            'message': message,
            'cloudinary_url': cloudinary_url,
            'timestamp': str(timezone.now())
        }
    
    def get_upload_results_json(self):
        """Get upload results as JSON for JavaScript"""
        if hasattr(self, '_upload_results'):
            return json.dumps(self._upload_results)
        return '{}'


def upload_to_cloudinary(file):
    """Upload file to Cloudinary and return the URL"""
    try:
        # Configure Cloudinary (same pattern as blog)
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.getenv("CLOUDINARY_API_KEY", ""),
            api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
            secure=True,
        )

        # Determine resource type based on file extension
        file_name = getattr(file, "name", "")
        if file_name.lower().endswith((".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx")):
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
        import traceback

        print(f"Full traceback: {traceback.format_exc()}")
        return None


class MinuitesForm(AlertEnabledFormMixin, forms.ModelForm):
    class Meta:
        model = Minuites
        fields = ["title", "date", "minuites"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "minuites": AlertEnabledFileInput(attrs={"class": "form-control", "accept": ".pdf,.doc,.docx"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If a new file is uploaded, try to upload to Cloudinary
        if self.files.get("minuites"):
            uploaded_file = self.files["minuites"]
            cloudinary_url = upload_to_cloudinary(uploaded_file)
            if cloudinary_url:
                instance.minuites_url = cloudinary_url
                self.add_upload_result('minuites', True, 
                    f"Minutes document '{uploaded_file.name}' uploaded successfully to Cloudinary!", 
                    cloudinary_url)
                print(f"Minutes file uploaded to Cloudinary: {cloudinary_url}")
            else:
                self.add_upload_result('minuites', False,
                    f"Failed to upload '{uploaded_file.name}' to Cloudinary. File saved locally as backup.")
                print("Failed to upload to Cloudinary, file will be saved locally")

        if commit:
            instance.save()
        return instance


class FinancialCheckbookForm(AlertEnabledFormMixin, forms.ModelForm):
    class Meta:
        model = FinancialCheckbook
        fields = ["title", "date", "checkbook"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "checkbook": AlertEnabledFileInput(attrs={"class": "form-control", "accept": ".pdf,.xls,.xlsx"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If a new file is uploaded, try to upload to Cloudinary
        if self.files.get("checkbook"):
            uploaded_file = self.files["checkbook"]
            cloudinary_url = upload_to_cloudinary(uploaded_file)
            if cloudinary_url:
                instance.checkbook_url = cloudinary_url
                self.add_upload_result('checkbook', True,
                    f"Financial checkbook '{uploaded_file.name}' uploaded successfully to Cloudinary!",
                    cloudinary_url)
                print(f"Checkbook file uploaded to Cloudinary: {cloudinary_url}")
            else:
                self.add_upload_result('checkbook', False,
                    f"Failed to upload '{uploaded_file.name}' to Cloudinary. File saved locally as backup.")
                print("Failed to upload to Cloudinary, file will be saved locally")

        if commit:
            instance.save()
        return instance


def upload_image_to_cloudinary(image_file, folder="gallery"):
    """Upload image file to Cloudinary and return the URL"""
    try:
        # Configure Cloudinary (same pattern as blog)
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.getenv("CLOUDINARY_API_KEY", ""),
            api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
            secure=True,
        )

        # Upload the image
        result = cloudinary.uploader.upload(
            image_file,
            folder=folder,  # Upload to specified folder in Cloudinary
            resource_type="image",
            quality="auto",
            fetch_format="auto",
        )

        return result["secure_url"]
    except Exception as e:
        print(f"Cloudinary image upload error: {e}")
        return None


def upload_video_to_cloudinary(video_file, folder="gallery"):
    """Upload video file to Cloudinary and return the URL"""
    try:
        # Configure Cloudinary (same pattern as blog)
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.getenv("CLOUDINARY_API_KEY", ""),
            api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
            secure=True,
        )

        # Upload the video
        result = cloudinary.uploader.upload(
            video_file,
            folder=folder,  # Upload to specified folder in Cloudinary
            resource_type="video",
            quality="auto",
        )

        return result["secure_url"]
    except Exception as e:
        print(f"Cloudinary video upload error: {e}")
        return None


# Gallery Forms
class GalleryFolderForm(AlertEnabledFormMixin, forms.ModelForm):
    """Form for creating and editing gallery folders"""
    
    class Meta:
        model = GalleryFolder
        fields = ["name", "description", "cover_image", "is_active", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "cover_image": AlertEnabledFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If a new cover image is uploaded, try to upload to Cloudinary
        if self.files.get("cover_image"):
            uploaded_file = self.files["cover_image"]
            cloudinary_url = upload_image_to_cloudinary(uploaded_file, folder="gallery/covers")
            if cloudinary_url:
                instance.cover_image_url = cloudinary_url
                self.add_upload_result('cover_image', True,
                    f"Gallery folder cover image uploaded successfully to Cloudinary!",
                    cloudinary_url)
            else:
                self.add_upload_result('cover_image', False,
                    f"Failed to upload cover image to Cloudinary. Image saved locally as backup.")

        if commit:
            instance.save()
        return instance


class GalleryImageForm(AlertEnabledFormMixin, forms.ModelForm):
    """Form for uploading gallery images"""
    
    class Meta:
        model = GalleryImage
        fields = ["folder", "title", "alt_text", "image", "is_active", "order"]
        widgets = {
            "folder": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "alt_text": forms.TextInput(attrs={"class": "form-control"}),
            "image": AlertEnabledFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If a new image is uploaded, try to upload to Cloudinary
        if self.files.get("image"):
            uploaded_file = self.files["image"]
            cloudinary_url = upload_image_to_cloudinary(uploaded_file, folder="gallery/images")
            if cloudinary_url:
                instance.image_url = cloudinary_url
                self.add_upload_result('image', True,
                    f"Gallery image '{uploaded_file.name}' uploaded successfully to Cloudinary with optimization!",
                    cloudinary_url)
            else:
                self.add_upload_result('image', False,
                    f"Failed to upload '{uploaded_file.name}' to Cloudinary. Image was NOT saved.")
                raise forms.ValidationError(f"Failed to upload '{uploaded_file.name}' to Cloudinary. Please try again.")

        if commit:
            instance.save()
        return instance


class GalleryVideoForm(AlertEnabledFormMixin, forms.ModelForm):
    """Form for uploading gallery videos"""
    
    class Meta:
        model = GalleryVideo
        fields = ["folder", "title", "video", "thumbnail", "is_active", "order", "uploaded_by"]
        widgets = {
            "folder": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "video": AlertEnabledFileInput(attrs={"class": "form-control", "accept": "video/*"}),
            "thumbnail": AlertEnabledFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "uploaded_by": forms.TextInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        upload_results = []

        # If a new video is uploaded, try to upload to Cloudinary
        if self.files.get("video"):
            uploaded_file = self.files["video"]
            cloudinary_url = upload_video_to_cloudinary(uploaded_file, folder="gallery/videos")
            if cloudinary_url:
                instance.video_url = cloudinary_url
                self.add_upload_result('video', True,
                    f"Gallery video '{uploaded_file.name}' uploaded successfully to Cloudinary!",
                    cloudinary_url)
                upload_results.append("video uploaded")
            else:
                self.add_upload_result('video', False,
                    f"Failed to upload video '{uploaded_file.name}' to Cloudinary. Video saved locally as backup.")

        # If a new thumbnail is uploaded, try to upload to Cloudinary
        if self.files.get("thumbnail"):
            uploaded_file = self.files["thumbnail"]
            cloudinary_url = upload_image_to_cloudinary(uploaded_file, folder="gallery/thumbnails")
            if cloudinary_url:
                instance.thumbnail_url = cloudinary_url
                self.add_upload_result('thumbnail', True,
                    f"Video thumbnail uploaded successfully to Cloudinary!",
                    cloudinary_url)
                upload_results.append("thumbnail uploaded")
            else:
                self.add_upload_result('thumbnail', False,
                    f"Failed to upload thumbnail to Cloudinary. Thumbnail saved locally as backup.")

        # Add combined success message if multiple files uploaded
        if len(upload_results) > 1:
            self.add_upload_result('combined', True,
                f"Gallery video with thumbnail uploaded successfully! ({', '.join(upload_results)})")

        if commit:
            instance.save()
        return instance


class TestimonialForm(AlertEnabledFormMixin, forms.ModelForm):
    """Form for creating and editing testimonials"""
    
    class Meta:
        model = Testimonial
        fields = ["name", "title", "content", "image", "is_active", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "image": AlertEnabledFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If a new image is uploaded, try to upload to Cloudinary
        if self.files.get("image"):
            uploaded_file = self.files["image"]
            cloudinary_url = upload_image_to_cloudinary(uploaded_file, folder="testimonials")
            if cloudinary_url:
                instance.image_url = cloudinary_url
                self.add_upload_result('image', True,
                    f"Testimonial image for '{instance.name}' uploaded successfully to Cloudinary!",
                    cloudinary_url)
            else:
                self.add_upload_result('image', False,
                    f"Failed to upload testimonial image to Cloudinary. Image saved locally as backup.")

        if commit:
            instance.save()
        return instance


class MembersGalleryImageForm(forms.ModelForm):
    def save(self, commit=True):
        instance = super().save(commit=False)
        # If a new image is uploaded, try to upload to Cloudinary
        if self.files.get("image"):
            uploaded_file = self.files["image"]
            cloudinary_url = upload_image_to_cloudinary(uploaded_file, folder="members_gallery/images")
            if cloudinary_url:
                instance.image_url = cloudinary_url
        if commit:
            instance.save()
        return instance
    class Meta:
        model = MembersGalleryImage
        fields = [
            'name',
            'description',
            'image',
            'alt_text',
            'is_active',
            'order'
        ]
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Optional description'}),
            'alt_text': forms.TextInput(attrs={'placeholder': 'Accessibility alt text'}),
        }
