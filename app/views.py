from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from umuahia_ireland.config import APP_NAME
from .models import Testimonial, GalleryFolder, GalleryImage, GalleryVideo

# Import blog models
try:
    from blog.models import BlogPost
except ImportError:
    BlogPost = None


# Create your views here.
def home(request):
    context = {}
    # Read cookie consent value
    cookie_consent = request.COOKIES.get('cookie_consent', None)
    context['cookie_consent'] = cookie_consent

    # Get active testimonials
    try:
        testimonials = Testimonial.objects.filter(is_active=True)
        context["testimonials"] = testimonials
    except Exception:
        # If there's any error (like table doesn't exist), just continue without testimonials
        context["testimonials"] = []

    # Get latest blog posts if blog app is available
    if BlogPost:
        try:
            latest_posts = (
                BlogPost.objects.filter(status="published")
                .select_related("author", "category")
                .prefetch_related("tags")
                .order_by("-published_at")[:4]
            )
            context["latest_posts"] = latest_posts
        except Exception:
            # If there's any error (like table doesn't exist), just continue without blog posts
            context["latest_posts"] = []
    else:
        context["latest_posts"] = []

    return render(request, "index.html", context)


def gallery_folders(request):
    """Display all active gallery folders."""
    folders = GalleryFolder.objects.filter(is_active=True).order_by('order', 'name')
    
    # Add media counts for each folder
    for folder in folders:
        folder.image_count = folder.images.filter(is_active=True).count()
        folder.video_count = folder.videos.filter(is_active=True).count()
        folder.total_media_count = folder.image_count + folder.video_count
    
    context = {
        'folders': folders,
        'page_title': 'Gallery'
    }
    return render(request, "gallery/folders.html", context)


def gallery_folder_detail(request, folder_slug):
    """Display mixed media (images and videos) in a specific gallery folder."""
    folder = get_object_or_404(GalleryFolder, slug=folder_slug, is_active=True)
    
    # Get active images and videos for this folder
    images = folder.images.filter(is_active=True).order_by('order', 'created_at')
    videos = folder.videos.filter(is_active=True).order_by('order', 'created_at')
    
    # Get mixed media sorted by created_at
    mixed_media = folder.get_latest_media(limit=None)  # Get all media, sorted
    
    context = {
        'folder': folder,
        'images': images,
        'videos': videos,
        'mixed_media': mixed_media,
        'page_title': f'Gallery - {folder.name}'
    }
    return render(request, "gallery/folder_detail.html", context)
