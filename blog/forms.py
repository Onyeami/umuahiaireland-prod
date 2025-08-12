from django import forms
from django.forms import inlineformset_factory
from .models import BlogPost, BlogImage, Comment, Category, Tag
import cloudinary
import cloudinary.uploader
from django.conf import settings
import os


def upload_to_cloudinary(image_file):
    """Upload image file to Cloudinary and return the URL"""
    try:
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.getenv("CLOUDINARY_API_KEY", ""),
            api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
            secure=True,
        )

        # Upload the image
        result = cloudinary.uploader.upload(
            image_file,
            folder="blog",  # Upload to blog folder in Cloudinary
            resource_type="image",
            quality="auto",
            fetch_format="auto",
        )

        return result["secure_url"]
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None


class BlogPostForm(forms.ModelForm):
    """Form for creating and editing blog posts"""

    # Add a file field for uploading featured image
    featured_image_file = forms.ImageField(
        required=False,
        help_text="Upload featured image (will be uploaded to Cloudinary)",
        widget=forms.FileInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100",
                "accept": "image/*",
            }
        ),
    )

    class Meta:
        model = BlogPost
        fields = [
            "title",
            "category",
            "tags",
            "excerpt",
            "content",
            "featured_image_file",  # This will show the file upload field
            "meta_title",
            "meta_description",
            "status",
            "is_featured",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Enter blog post title",
                }
            ),
            "excerpt": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Brief description of the post",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 editor",
                    "id": "editor",
                    "rows": 15,
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "tags": forms.CheckboxSelectMultiple(attrs={"class": "space-y-2"}),
            "meta_title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "SEO title (optional)",
                }
            ),
            "meta_description": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 2,
                    "placeholder": "SEO description (optional)",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "is_featured": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                }
            ),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle featured image upload
        featured_image_file = self.cleaned_data.get("featured_image_file")
        if featured_image_file:
            cloudinary_url = upload_to_cloudinary(featured_image_file)
            if cloudinary_url:
                instance.featured_image = cloudinary_url

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class BlogImageForm(forms.ModelForm):
    """Form for blog images"""

    # Add a file field for uploading images
    image_file = forms.ImageField(
        required=False,
        help_text="Upload image (will be uploaded to Cloudinary)",
        widget=forms.FileInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100",
                "accept": "image/*",
            }
        ),
    )

    class Meta:
        model = BlogImage
        fields = [
            "image_file",
            "caption",
            "alt_text",
            "order",
        ]  # Include the file upload field
        widgets = {
            "caption": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Image caption (optional)",
                }
            ),
            "alt_text": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Alt text for accessibility",
                }
            ),
            "order": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "min": 0,
                }
            ),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle image upload
        image_file = self.cleaned_data.get("image_file")
        if image_file:
            cloudinary_url = upload_to_cloudinary(image_file)
            if cloudinary_url:
                instance.image = cloudinary_url

        if commit:
            instance.save()

        return instance


# Create formset for multiple images
BlogImageFormSet = inlineformset_factory(
    BlogPost, BlogImage, form=BlogImageForm, extra=3, can_delete=True
)


class CommentForm(forms.ModelForm):
    """Form for user comments"""

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 4,
                    "placeholder": "Write your comment here...",
                }
            )
        }


class GuestCommentForm(forms.ModelForm):
    """Form for guest comments"""

    class Meta:
        model = Comment
        fields = ["guest_name", "guest_email", "content"]
        widgets = {
            "guest_name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Your name",
                }
            ),
            "guest_email": forms.EmailInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Your email (optional)",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 4,
                    "placeholder": "Write your comment here...",
                }
            ),
        }


class CategoryForm(forms.ModelForm):
    """Form for creating categories"""

    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Category name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Category description (optional)",
                }
            ),
        }


class TagForm(forms.ModelForm):
    """Form for creating tags"""

    class Meta:
        model = Tag
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Tag name",
                }
            )
        }


class BlogSearchForm(forms.Form):
    """Form for searching blog posts"""

    query = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                "placeholder": "Search posts...",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            }
        ),
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="All Tags",
        widget=forms.Select(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            }
        ),
    )
