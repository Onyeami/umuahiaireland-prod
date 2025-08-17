from django.db import models
import uuid
from django.utils import timezone


# Create your models here.
class Minuites(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
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
