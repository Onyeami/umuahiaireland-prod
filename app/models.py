from django.db import models
import uuid
from django.utils import timezone


# Create your models here.
class Minuites(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    date = models.DateField()
    minuites = models.FileField(upload_to="minuites/", blank=True, null=True)
    minuites_url = models.URLField(
        blank=True, help_text="Cloudinary URL for the minutes file"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class FinancialCheckbook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, blank=True, default="")
    date = models.DateField(default=timezone.now)
    checkbook = models.FileField(upload_to="checkbooks/", blank=True, null=True)
    checkbook_url = models.URLField(
        blank=True, help_text="Cloudinary URL for the checkbook file"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Checkbook {self.id}"


class Testimonial(models.Model):
    """Model for storing testimonials"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    title = models.CharField(
        max_length=200, blank=True, help_text="e.g., 'Work Programmes Graduate'"
    )
    content = models.TextField()
    image = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(
        default=0, help_text="Order of display (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} - {self.title}"


class GalleryFolder(models.Model):
    """Model for organizing gallery images into folders/albums"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100, 
        help_text="Folder name (e.g., '2025 Picnic Event', 'Monthly Meetings')"
    )
    slug = models.SlugField(
        max_length=100, 
        unique=True, 
        blank=True,
        help_text="URL-friendly version of the name (auto-generated)"
    )
    description = models.TextField(
        blank=True, 
        help_text="Optional description of this folder/event"
    )
    cover_image = models.ImageField(
        upload_to="gallery/covers/", 
        blank=True, 
        null=True,
        help_text="Main image to represent this folder"
    )
    cover_image_url = models.URLField(
        blank=True, 
        help_text="Cloudinary URL for the cover image"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this folder should be visible to the public"
    )
    order = models.PositiveIntegerField(
        default=0, 
        help_text="Order of display (lower numbers appear first)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Gallery Folder"
        verbose_name_plural = "Gallery Folders"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_image_count(self):
        """Return the number of images in this folder"""
        return self.images.filter(is_active=True).count()

    def get_latest_images(self, limit=4):
        """Get the latest images from this folder for preview"""
        return self.images.filter(is_active=True).order_by('-created_at')[:limit]

    def get_cover_image(self):
        """Get the cover image - uses the image with lowest order number"""
        # First try to get the image with the lowest order number
        cover_image = self.images.filter(is_active=True).order_by('order', 'created_at').first()
        
        # If no images in folder, return None
        if not cover_image:
            return None
            
        return cover_image

    def get_cover_image_url(self):
        """Get the cover image URL for display"""
        cover_image = self.get_cover_image()
        if cover_image and cover_image.image:
            return cover_image.image.url
        return None


class GalleryImage(models.Model):
    """Model for individual gallery images"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(
        GalleryFolder, 
        on_delete=models.CASCADE, 
        related_name='images',
        help_text="Which folder this image belongs to"
    )
    title = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Optional title/caption for the image"
    )
    image = models.ImageField(
        upload_to="gallery/images/", 
        help_text="The actual image file"
    )
    image_url = models.URLField(
        blank=True, 
        help_text="Cloudinary URL for the image"
    )
    alt_text = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Alternative text for accessibility"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether this image should be visible to the public"
    )
    order = models.PositiveIntegerField(
        default=0, 
        help_text="Order of display within the folder"
    )
    uploaded_by = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Optional: Who uploaded this image"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"

    def __str__(self):
        return self.title or f"Image in {self.folder.name}"
