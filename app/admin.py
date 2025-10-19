from django.contrib import admin
from django.utils.html import format_html
from .models import Minuites, FinancialCheckbook, Testimonial, GalleryFolder, GalleryImage, GalleryVideo, MembersGalleryImage
from .forms import MinuitesForm, FinancialCheckbookForm, TestimonialForm, GalleryFolderForm, GalleryImageForm, GalleryVideoForm

# Register your models here.
@admin.register(Minuites)
class MinuitesAdmin(admin.ModelAdmin):
    form = MinuitesForm
    list_display = ('title', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title',)
    date_hierarchy = 'created_at'


@admin.register(FinancialCheckbook)
class FinancialCheckbookAdmin(admin.ModelAdmin):
    form = FinancialCheckbookForm
    list_display = ('title', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title',)
    date_hierarchy = 'created_at'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    form = TestimonialForm
    list_display = ('name', 'title', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'title', 'content')
    list_editable = ('is_active', 'order')
    ordering = ('order', '-created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'title', 'content')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
    )


class GalleryImageInline(admin.TabularInline):
    """Inline admin for gallery images within folder admin"""
    model = GalleryImage
    extra = 0
    fields = ('title', 'image', 'alt_text', 'is_active', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        # Use Cloudinary URL if available, otherwise local file
        image_url = obj.image_url if obj.image_url else (obj.image.url if obj.image and hasattr(obj.image, 'url') else None)
        
        if image_url:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                image_url
            )
        return "No image"
    image_preview.short_description = "Preview"


class GalleryVideoInline(admin.TabularInline):
    """Inline admin for gallery videos within folder admin"""
    model = GalleryVideo
    extra = 0
    fields = ('title', 'video', 'thumbnail', 'is_active', 'order')
    readonly_fields = ('video_preview', 'file_size_display')
    
    def video_preview(self, obj):
        # Use Cloudinary thumbnail URL if available, otherwise local file
        thumbnail_url = obj.thumbnail_url if obj.thumbnail_url else (obj.thumbnail.url if obj.thumbnail and hasattr(obj.thumbnail, 'url') else None)
        
        if thumbnail_url:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                thumbnail_url
            )
        elif obj.video or obj.video_url:
            return format_html(
                '<div style="background: #f8f9fa; border: 2px solid #dee2e6; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; border-radius: 4px;">'
                '<span style="font-size: 16px;">🎥</span>'
                '</div>'
            )
        return "No video"
    video_preview.short_description = "Preview"
    
    def file_size_display(self, obj):
        return obj.get_file_size_display() if obj.file_size else "Unknown"
    file_size_display.short_description = "Size"


@admin.register(GalleryFolder)
class GalleryFolderAdmin(admin.ModelAdmin):
    form = GalleryFolderForm
    list_display = ('name', 'slug', 'cover_image_display', 'image_count_display', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'order')
    ordering = ('order', '-created_at')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [GalleryImageInline, GalleryVideoInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order'),
            'description': 'Cover image is automatically selected from the first image (lowest order) in this folder'
        }),
    )
    
    def image_count_display(self, obj):
        image_count = obj.get_image_count()
        video_count = obj.get_video_count()
        total_count = image_count + video_count
        
        if total_count > 0:
            return format_html(
                '<span style="color: #28a745;">{} images, {} videos</span>',
                image_count, video_count
            )
        else:
            return format_html('<span style="color: #dc3545;">No media</span>')
    image_count_display.short_description = "Media Count"
    image_count_display.admin_order_field = 'images__count'

    def cover_image_display(self, obj):
        """Display the automatic cover image preview"""
        cover_url = obj.get_cover_image_url()
        if cover_url:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                cover_url
            )
        return format_html('<span style="color: #6c757d;">No images</span>')
    cover_image_display.short_description = "Cover Image"
    
    def get_queryset(self, request):
        """Optimize queryset to include image count"""
        qs = super().get_queryset(request)
        qs = qs.prefetch_related('images')
        return qs


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    form = GalleryImageForm
    list_display = ('title_display', 'folder', 'image_preview', 'is_active', 'order', 'created_at')
    list_filter = ('folder', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title', 'alt_text', 'folder__name')
    list_editable = ('is_active', 'order')
    ordering = ('folder', 'order', '-created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('folder', 'title', 'alt_text')
        }),
        ('Image', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image or provide Cloudinary URL'
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
        ('Metadata', {
            'fields': ('uploaded_by',),
            'classes': ('collapse',)
        }),
    )
    
    def title_display(self, obj):
        return obj.title or f"Image #{str(obj.id)[:8]}"
    title_display.short_description = "Title"
    
    def image_preview(self, obj):
        # Use Cloudinary URL if available, otherwise local file
        image_url = obj.image_url if obj.image_url else (obj.image.url if obj.image and hasattr(obj.image, 'url') else None)
        
        if image_url:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px; border-radius: 4px;" />',
                image_url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(MembersGalleryImage)
class MembersGalleryImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_preview', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'alt_text')
    list_editable = ('is_active', 'order')
    ordering = ('order', '-created_at')
    fieldsets = (
        ('Member Info', {
            'fields': ('name', 'description')
        }),
        ('Image', {
            'fields': ('image', 'image_url', 'alt_text'),
            'description': 'Upload a member photo or provide Cloudinary URL'
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
        ('Metadata', {
            'fields': ('uploaded_by',),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        image_url = obj.image_url if obj.image_url else (obj.image.url if obj.image and hasattr(obj.image, 'url') else None)
        if image_url:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 60px; border-radius: 4px;" />', image_url)
        return "No image"
    image_preview.short_description = "Preview"
