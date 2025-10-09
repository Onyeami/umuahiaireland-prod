from django.contrib import admin
from django.utils.html import format_html
from .models import Minuites, FinancialCheckbook, Testimonial, GalleryFolder, GalleryImage

# Register your models here.
@admin.register(Minuites)
class MinuitesAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title',)
    date_hierarchy = 'created_at'


@admin.register(FinancialCheckbook)
class FinancialCheckbookAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title',)
    date_hierarchy = 'created_at'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
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
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url if hasattr(obj.image, 'url') else ''
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(GalleryFolder)
class GalleryFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'cover_image_display', 'image_count_display', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'order')
    ordering = ('order', '-created_at')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [GalleryImageInline]
    
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
        count = obj.get_image_count()
        return format_html(
            '<span style="color: {};">{} images</span>',
            '#28a745' if count > 0 else '#dc3545',
            count
        )
    image_count_display.short_description = "Images"
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
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 60px; border-radius: 4px;" />',
                obj.image.url if hasattr(obj.image, 'url') else ''
            )
        return "No image"
    image_preview.short_description = "Preview"
