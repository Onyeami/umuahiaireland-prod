from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.conf import settings
import logging
from .models import BlogPost, Category, Tag, Comment, BlogSettings
from .forms import (
    BlogPostForm,
    BlogImageFormSet,
    CommentForm,
    GuestCommentForm,
    CategoryForm,
    TagForm,
    BlogSearchForm,
)

User = get_user_model()
logger = logging.getLogger(__name__)


def _is_cloudinary_configured():
    """Check if Cloudinary is properly configured"""
    if settings.DEBUG:
        return False

    try:
        return (
            hasattr(settings, "DEFAULT_FILE_STORAGE")
            and "cloudinary" in settings.DEFAULT_FILE_STORAGE.lower()
        )
    except:
        return False


def is_admin_user(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# Public Blog Views
class BlogListView(ListView):
    """List all published blog posts"""

    model = BlogPost
    template_name = "blog/blog_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            BlogPost.objects.filter(status="published")
            .select_related("author", "category")
            .prefetch_related("tags")
        )

        # Search functionality
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(excerpt__icontains=query)
            )

        # Category filter
        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Tag filter
        tag_slug = self.request.GET.get("tag")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.annotate(
            post_count=Count("posts")
        ).filter(post_count__gt=0)
        context["tags"] = Tag.objects.annotate(post_count=Count("posts")).filter(
            post_count__gt=0
        )
        context["featured_posts"] = BlogPost.objects.filter(
            status="published", is_featured=True
        )[:3]
        context["search_form"] = BlogSearchForm(self.request.GET)
        return context


class BlogDetailView(DetailView):
    """Display a single blog post"""

    model = BlogPost
    template_name = "blog/blog_detail.html"
    context_object_name = "post"
    slug_field = "slug"

    def get_queryset(self):
        return (
            BlogPost.objects.filter(status="published")
            .select_related("author", "category")
            .prefetch_related("tags", "images")
        )

    def get_object(self):
        obj = super().get_object()
        # Increment view count
        obj.view_count += 1
        obj.save(update_fields=["view_count"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

        # Get approved comments
        comments = post.comments.filter(status="approved", parent=None).select_related(
            "author"
        )
        context["comments"] = comments
        context["comment_form"] = CommentForm()
        context["guest_comment_form"] = GuestCommentForm()

        # Related posts
        context["related_posts"] = BlogPost.objects.filter(
            status="published", category=post.category
        ).exclude(id=post.id)[:3]

        # In your blog detail view
        if post.category:
            category_posts = BlogPost.objects.filter(
                category=post.category, status="published"
            ).exclude(id=post.id)[
                :5
            ]  # Show 5 related posts
        else:
            category_posts = None

        context["category_posts"] = category_posts

        return context


def blog_search(request):
    """Search blog posts"""
    form = BlogSearchForm(request.GET)
    posts = BlogPost.objects.filter(status="published")

    if form.is_valid():
        query = form.cleaned_data.get("query")
        category = form.cleaned_data.get("category")
        tag = form.cleaned_data.get("tag")

        if query:
            posts = posts.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(excerpt__icontains=query)
            )

        if category:
            posts = posts.filter(category=category)

        if tag:
            posts = posts.filter(tags=tag)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "posts": page_obj,
        "form": form,
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
    }
    return render(request, "blog/blog_search.html", context)


def category_posts(request, slug):
    """Posts by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(status="published", category=category)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "posts": page_obj,
    }
    return render(request, "blog/category_posts.html", context)


def tag_posts(request, slug):
    """Posts by tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(status="published", tags=tag)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "tag": tag,
        "posts": page_obj,
    }
    return render(request, "blog/tag_posts.html", context)


@login_required
def add_comment(request, slug):
    """Add comment to blog post"""
    post = get_object_or_404(BlogPost, slug=slug, status="published")

    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(
                    request, "Your comment has been submitted and is awaiting approval."
                )
        else:
            form = GuestCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.save()
                messages.success(
                    request, "Your comment has been submitted and is awaiting approval."
                )

    return redirect("blog:post_detail", slug=slug)


# Admin Blog Views
@user_passes_test(is_admin_user)
def admin_blog_dashboard(request):
    """Admin blog dashboard"""
    context = {
        "total_posts": BlogPost.objects.count(),
        "published_posts": BlogPost.objects.filter(status="published").count(),
        "draft_posts": BlogPost.objects.filter(status="draft").count(),
        "pending_comments": Comment.objects.filter(status="pending").count(),
        "recent_posts": BlogPost.objects.all()[:5],
        "recent_comments": Comment.objects.filter(status="pending")[:5],
    }
    return render(request, "blog/admin/dashboard.html", context)


@user_passes_test(is_admin_user)
def admin_post_list(request):
    """Admin post list"""
    posts = BlogPost.objects.all().select_related("author", "category")

    # Filter by status
    status = request.GET.get("status")
    if status:
        posts = posts.filter(status=status)

    paginator = Paginator(posts, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "posts": page_obj,
        "current_status": status,
    }
    return render(request, "blog/admin/post_list.html", context)


@user_passes_test(is_admin_user)
@user_passes_test(is_admin_user)
def admin_create_post(request):
    """Create new blog post"""
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        formset = BlogImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                form.save_m2m()  # Save many-to-many relationships

                # Handle featured image
                if post.featured_image:
                    logger.info(
                        f"Featured image uploaded for post '{post.title}': {post.featured_image}"
                    )
                    messages.info(request, f"Featured image uploaded to Cloudinary")

                # Handle additional images
                formset.instance = post
                saved_images = formset.save()

                if saved_images:
                    logger.info(
                        f"Additional images uploaded for post '{post.title}': {len(saved_images)} images"
                    )
                    for img in saved_images:
                        logger.info(f"Image URL: {img.image}")
                    messages.info(
                        request,
                        f"{len(saved_images)} additional images uploaded to Cloudinary",
                    )

                messages.success(
                    request, f"Blog post '{post.title}' created successfully!"
                )

                return redirect("blog:admin_post_list")

            except Exception as e:
                logger.error(f"Error creating blog post: {str(e)}")
                messages.error(request, f"Error creating blog post: {str(e)}")
        else:
            # Log form errors for debugging
            if not form.is_valid():
                logger.error(f"Blog post form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            if not formset.is_valid():
                logger.error(f"Image formset errors: {formset.errors}")
                for form_error in formset.errors:
                    if form_error:
                        for field, errors in form_error.items():
                            for error in errors:
                                messages.error(request, f"Image {field}: {error}")
    else:
        form = BlogPostForm()
        formset = BlogImageFormSet()

    context = {
        "form": form,
        "formset": formset,
        "title": "Create New Post",
        "debug_mode": settings.DEBUG,
        "cloudinary_configured": _is_cloudinary_configured(),
    }
    return render(request, "blog/admin/post_form.html", context)


@user_passes_test(is_admin_user)
def admin_edit_post(request, slug):
    """Edit existing blog post"""
    post = get_object_or_404(BlogPost, slug=slug)

    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        formset = BlogImageFormSet(request.POST, request.FILES, instance=post)

        if form.is_valid() and formset.is_valid():
            try:
                updated_post = form.save()

                # Handle featured image updates
                if updated_post.featured_image:
                    logger.info(
                        f"Featured image updated for post '{updated_post.title}': {updated_post.featured_image}"
                    )
                    messages.info(request, "Featured image updated in Cloudinary")

                # Handle additional images
                saved_images = formset.save()

                if saved_images:
                    logger.info(
                        f"Additional images updated for post '{updated_post.title}': {len(saved_images)} images"
                    )
                    for img in saved_images:
                        logger.info(f"Image URL: {img.image}")
                    messages.info(
                        request,
                        f"{len(saved_images)} additional images updated in Cloudinary",
                    )

                messages.success(
                    request, f"Blog post '{updated_post.title}' updated successfully!"
                )

                return redirect("blog:admin_post_list")

            except Exception as e:
                logger.error(f"Error updating blog post: {str(e)}")
                messages.error(request, f"Error updating blog post: {str(e)}")
        else:
            # Log form errors for debugging
            if not form.is_valid():
                logger.error(f"Blog post form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            if not formset.is_valid():
                logger.error(f"Image formset errors: {formset.errors}")
                for form_error in formset.errors:
                    if form_error:
                        for field, errors in form_error.items():
                            for error in errors:
                                messages.error(request, f"Image {field}: {error}")
    else:
        form = BlogPostForm(instance=post)
        formset = BlogImageFormSet(instance=post)

    context = {
        "form": form,
        "formset": formset,
        "post": post,
        "title": f"Edit: {post.title}",
        "debug_mode": settings.DEBUG,
        "cloudinary_configured": _is_cloudinary_configured(),
    }
    return render(request, "blog/admin/post_form.html", context)


# Public views
@user_passes_test(is_admin_user)
def admin_delete_post(request, slug):
    """Delete blog post"""
    post = get_object_or_404(BlogPost, slug=slug)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Blog post deleted successfully!")
        return redirect("blog:admin_post_list")

    context = {"post": post}
    return render(request, "blog/admin/post_confirm_delete.html", context)


@user_passes_test(is_admin_user)
def admin_comment_list(request):
    """Admin comment management"""
    comments = Comment.objects.all().select_related("post", "author")

    # Filter by status
    status = request.GET.get("status")
    if status:
        comments = comments.filter(status=status)

    paginator = Paginator(comments, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "comments": page_obj,
        "current_status": status,
    }
    return render(request, "blog/admin/comment_list.html", context)


@user_passes_test(is_admin_user)
def admin_comment_action(request, comment_id, action):
    """Approve/reject comments"""
    comment = get_object_or_404(Comment, id=comment_id)

    if action == "approve":
        comment.status = "approved"
        messages.success(request, "Comment approved!")
    elif action == "reject":
        comment.status = "rejected"
        messages.success(request, "Comment rejected!")

    comment.save()
    return redirect("blog:admin_comment_list")


@user_passes_test(is_admin_user)
def admin_manage_categories(request):
    """Manage blog categories"""
    categories = Category.objects.all()

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect("blog:admin_manage_categories")
    else:
        form = CategoryForm()

    context = {
        "categories": categories,
        "form": form,
    }
    return render(request, "blog/admin/manage_categories.html", context)


@user_passes_test(is_admin_user)
def admin_manage_tags(request):
    """Manage blog tags"""
    tags = Tag.objects.all()

    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag created successfully!")
            return redirect("blog:admin_manage_tags")
    else:
        form = TagForm()

    context = {
        "tags": tags,
        "form": form,
    }
    return render(request, "blog/admin/manage_tags.html", context)


@user_passes_test(is_admin_user)
def admin_media_debug(request):
    """Debug media configuration"""
    import os

    debug_info = {
        "django_debug": settings.DEBUG,
        "media_url": settings.MEDIA_URL,
        "media_root": str(settings.MEDIA_ROOT),
        "cloudinary_configured": _is_cloudinary_configured(),
    }

    # Check environment variables
    env_vars = {
        "CLOUDINARY_CLOUD_NAME": bool(os.getenv("CLOUDINARY_CLOUD_NAME")),
        "CLOUDINARY_API_KEY": bool(os.getenv("CLOUDINARY_API_KEY")),
        "CLOUDINARY_API_SECRET": bool(os.getenv("CLOUDINARY_API_SECRET")),
    }

    # Check storage backend
    storage_info = {}
    if hasattr(settings, "DEFAULT_FILE_STORAGE"):
        storage_info["storage_backend"] = settings.DEFAULT_FILE_STORAGE
    else:
        storage_info["storage_backend"] = "Default Django Storage"

    # Get recent posts with images for testing
    recent_posts = BlogPost.objects.filter(featured_image__isnull=False).order_by(
        "-created_at"
    )[:5]

    context = {
        "debug_info": debug_info,
        "env_vars": env_vars,
        "storage_info": storage_info,
        "recent_posts": recent_posts,
    }
    return render(request, "blog/admin/media_debug.html", context)
