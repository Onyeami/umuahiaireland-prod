# Import required generic views
from django.views.generic import ListView, View
from app.forms import MembersGalleryImageForm
# ...existing code...

# Place MembersGalleryImage views after AdminRequiredMixin definition

from app.models import MembersGalleryImage

class MembersGalleryImageListView(ListView):
    model = MembersGalleryImage
    template_name = "_admin/members_gallery.html"
    context_object_name = "images"

    def get_queryset(self):
        return MembersGalleryImage.objects.order_by('order', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_images'] = self.get_queryset().count()
        return context

class MembersGalleryImageCreateView(View):
    def get(self, request):
        form = MembersGalleryImageForm()
        return render(request, '_admin/create_member_image.html', {'form': form})

    def post(self, request):
        form = MembersGalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            member_image = form.save(commit=False)
            member_image.uploaded_by = request.user.email
            member_image.save()
            messages.success(request, 'Member image uploaded successfully.')
            return redirect('admin:members_gallery')
        messages.error(request, 'Error uploading member image. Please check your inputs.')
        return render(request, '_admin/create_member_image.html', {'form': form})

class MembersGalleryImageEditView(View):
    def get(self, request, image_id):
        image = get_object_or_404(MembersGalleryImage, id=image_id)
        form = MembersGalleryImageForm(instance=image)
        return render(request, '_admin/edit_member_image.html', {'form': form, 'image': image})

    def post(self, request, image_id):
        image = get_object_or_404(MembersGalleryImage, id=image_id)
        form = MembersGalleryImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member image updated successfully.')
            return redirect('admin:members_gallery')
        messages.error(request, 'Error updating member image. Please check your inputs.')
        return render(request, '_admin/edit_member_image.html', {'form': form, 'image': image})

class MembersGalleryImageDeleteView(View):
    def post(self, request, image_id):
        image = get_object_or_404(MembersGalleryImage, id=image_id)
        image.delete()
        messages.success(request, 'Member image deleted successfully.')
        return redirect('admin:members_gallery')
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q, Count
from users.models import CustomUser
from app.models import Minuites, FinancialCheckbook, GalleryFolder, GalleryImage, GalleryVideo
from app.forms import MinuitesForm, FinancialCheckbookForm
from blog.models import BlogPost, Category, Tag, Comment, BlogSettings
from blog.forms import BlogPostForm, BlogImageFormSet, CategoryForm, TagForm
from django.core.exceptions import ValidationError


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class DashboardView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = "_admin/dashboard.html"
    context_object_name = "users"

    def get_queryset(self):
        return CustomUser.objects.all().order_by("-date_joined")[:5]



from app.models import MembersGalleryImage

class MembersGalleryImageListView(AdminRequiredMixin, ListView):
    model = MembersGalleryImage
    template_name = "_admin/members_gallery.html"
    context_object_name = "images"

    def get_queryset(self):
        return MembersGalleryImage.objects.order_by('order', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_images'] = self.get_queryset().count()
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_images"] = self.get_queryset().count()
        return context


class ProjectListView(AdminRequiredMixin, TemplateView):
    template_name = "_admin/projects.html"


class UserCreateView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            full_name = request.POST.get("full_name", "").strip()
            position = request.POST.get("position")
            password = request.POST.get("password")

            if not full_name:
                raise ValidationError("Full name is required")
            if not password:
                raise ValidationError("Password is required")

            name_parts = full_name.split()
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

            CustomUser.objects.create(
                email=request.POST.get("email"),
                first_name=first_name,
                last_name=last_name,
                position=position,
                is_active=True,
                is_staff=(position == "admin"),
                is_superuser=(position == "admin"),
                password=make_password(password),
            )

            return redirect("admin:dashboard")
        except ValidationError:
            return redirect("admin:dashboard")  # Optionally, add a message
        except Exception:
            return redirect("admin:dashboard")


class UserUpdateView(AdminRequiredMixin, View):
    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        return render(request, "_admin/edit_user.html", {"user": user})

    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)
        user.position = request.POST.get("position", user.position)
        user.save()
        messages.success(request, "User details updated successfully.")
        return redirect("admin:members")


class UserDeactivateView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_active:
            user.is_active = False
            user.save()
        return redirect("admin:members")


class UserActivateView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        if not user.is_active:
            user.is_active = True
            user.save()
        return redirect("admin:members")


class UserDeleteView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        get_object_or_404(CustomUser, id=user_id).delete()
        return redirect("admin:members")


class UserApproveView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_verified and not user.is_approved:
            user.is_approved = True
            user.save()

            # Send approval email
            try:
                from django.core.mail import send_mail
                from django.conf import settings

                subject = "Your Account Has Been Approved"
                message = f"""
                Dear {user.first_name} {user.last_name},

                Your account has been approved by an administrator. You can now log in to the system.

                Best regards,
                The Admin Team
                """

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the approval
                print(f"Failed to send approval email: {e}")

            messages.success(
                request, f"User {user.first_name} {user.last_name} has been approved."
            )
        else:
            messages.error(request, "User cannot be approved at this time.")

        return redirect("admin:members")


class UserRejectView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        if user.is_verified and user.is_approved:
            user.is_approved = False
            user.save()

            # Send rejection email
            try:
                from django.core.mail import send_mail
                from django.conf import settings

                subject = "Your Account Access Has Been Revoked"
                message = f"""
                Dear {user.first_name} {user.last_name},

                Your account access has been revoked by an administrator. You will no longer be able to log in to the system.

                If you believe this is an error, please contact the administrator.

                Best regards,
                The Admin Team
                """

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't fail the rejection
                print(f"Failed to send rejection email: {e}")

            messages.success(
                request, f"User {user.first_name} {user.last_name} has been rejected."
            )
        else:
            messages.error(request, "User cannot be rejected at this time.")

        return redirect("admin:members")


class MinuitesListView(AdminRequiredMixin, ListView):
    model = Minuites
    template_name = "_admin/minuites.html"
    context_object_name = "minuites"

    def get_queryset(self):
        return Minuites.objects.all().order_by("-created_at")


# Edit Minutes view
class EditMinuitesView(AdminRequiredMixin, View):
    def get(self, request, minuites_id):
        minuite = get_object_or_404(Minuites, id=minuites_id)
        form = MinuitesForm(instance=minuite)
        return render(
            request, "_admin/edit_minuites.html", {"minuite": minuite, "form": form}
        )

    def post(self, request, minuites_id):
        minuite = get_object_or_404(Minuites, id=minuites_id)
        form = MinuitesForm(request.POST, request.FILES, instance=minuite)
        if form.is_valid():
            form.save()
            messages.success(request, "Minutes updated successfully.")
        else:
            messages.error(request, "Error updating minutes. Please check your inputs.")
        return redirect("admin:minuites")


# Delete Minutes view
class DeleteMinuitesView(AdminRequiredMixin, View):
    def post(self, request, minuites_id):
        minuite = get_object_or_404(Minuites, id=minuites_id)
        minuite.delete()
        messages.success(request, "Minutes deleted successfully.")
        return redirect("admin:minuites")


class CreateMinuitesView(AdminRequiredMixin, View):
    def post(self, request):
        form = MinuitesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Minutes created successfully.")
        else:
            messages.error(request, "Error creating minutes. Please check your inputs.")
        return redirect("admin:minuites")


class SettingsView(AdminRequiredMixin, TemplateView):
    template_name = "_admin/settings.html"


class ChangePasswordView(AdminRequiredMixin, View):
    def post(self, request):
        current_password = request.POST.get("current-password")
        new_password = request.POST.get("new-password")
        confirm_password = request.POST.get("new-password2")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect!")
            return redirect("admin:settings")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("admin:settings")

        if new_password == current_password:
            messages.error(request, "The new password cannot be your current password!")
            return redirect("admin:settings")

        user.set_password(new_password)
        user.save()
        messages.success(
            request,
            "Your password has been changed! You will be redirected to login again",
        )
        return redirect("admin:settings")


class AdminResetUserPasswordView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        new_password = request.POST.get("new-password")
        confirm_password = request.POST.get("confirm-password")

        if not new_password or not confirm_password:
            messages.error(request, "Both password fields are required!")
            return redirect("admin:edit_user", user_id=user.id)

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("admin:edit_user", user_id=user.id)

        user.set_password(new_password)
        user.save()
        messages.success(
            request, f"Password for {user.email} has been reset successfully!"
        )
        return redirect("admin:edit_user", user_id=user.id)


class FinancialCheckbookListView(AdminRequiredMixin, ListView):
    model = FinancialCheckbook
    template_name = "_admin/financial_checkbook.html"
    context_object_name = "checkbook_list"

    def get_queryset(self):
        return FinancialCheckbook.objects.all().order_by("-created_at")


# Create Financial Checkbook Entry
class CreateFinancialCheckbookView(AdminRequiredMixin, View):
    def post(self, request):
        form = FinancialCheckbookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Financial checkbook entry added successfully.")
        else:
            messages.error(
                request,
                "Error creating financial checkbook entry. Please check your inputs.",
            )
        return redirect("admin:financial_checkbook")


# Edit Financial Checkbook Entry
class EditFinancialCheckbookView(AdminRequiredMixin, View):
    def get(self, request, checkbook_id):
        checkbook_entry = get_object_or_404(FinancialCheckbook, id=checkbook_id)
        form = FinancialCheckbookForm(instance=checkbook_entry)
        return render(
            request,
            "_admin/edit_financial_checkbook.html",
            {"checkbook": checkbook_entry, "form": form},
        )

    def post(self, request, checkbook_id):
        checkbook_entry = get_object_or_404(FinancialCheckbook, id=checkbook_id)
        form = FinancialCheckbookForm(
            request.POST, request.FILES, instance=checkbook_entry
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Financial checkbook entry updated successfully.")
        else:
            messages.error(
                request,
                "Error updating financial checkbook entry. Please check your inputs.",
            )
        return redirect("admin:financial_checkbook")


# Delete Financial Checkbook Entry
class DeleteFinancialCheckbookView(AdminRequiredMixin, View):
    def post(self, request, checkbook_id):
        checkbook_entry = get_object_or_404(FinancialCheckbook, id=checkbook_id)
        checkbook_entry.delete()
        messages.success(request, "Financial checkbook entry deleted successfully.")
        return redirect("admin:financial_checkbook")


# Blog Admin Views
class BlogDashboardView(AdminRequiredMixin, TemplateView):
    """Blog admin dashboard"""

    template_name = "_admin/blog/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "total_posts": BlogPost.objects.count(),
                "published_posts": BlogPost.objects.filter(status="published").count(),
                "draft_posts": BlogPost.objects.filter(status="draft").count(),
                "pending_comments": Comment.objects.filter(status="pending").count(),
                "recent_posts": BlogPost.objects.all()[:5],
                "recent_comments": Comment.objects.filter(status="pending")[:5],
            }
        )
        return context


class BlogPostListView(AdminRequiredMixin, ListView):
    """Admin blog post list"""

    model = BlogPost
    template_name = "_admin/blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        queryset = BlogPost.objects.all().select_related("author", "category")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_status"] = self.request.GET.get("status")
        return context


class BlogPostCreateView(AdminRequiredMixin, View):
    """Create new blog post"""

    def get(self, request):
        form = BlogPostForm()
        formset = BlogImageFormSet()
        context = {
            "form": form,
            "formset": formset,
            "title": "Create New Post",
        }
        return render(request, "_admin/blog/post_form.html", context)

    def post(self, request):
        form = BlogPostForm(request.POST, request.FILES)
        formset = BlogImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()

            formset.instance = post
            formset.save()

            messages.success(request, "Blog post created successfully!")
            return redirect("admin:blog_posts")

        context = {
            "form": form,
            "formset": formset,
            "title": "Create New Post",
        }
        return render(request, "_admin/blog/post_form.html", context)


class BlogPostEditView(AdminRequiredMixin, View):
    """Edit existing blog post"""

    def get(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug)
        form = BlogPostForm(instance=post)
        formset = BlogImageFormSet(instance=post)
        context = {
            "form": form,
            "formset": formset,
            "post": post,
            "title": f"Edit: {post.title}",
        }
        return render(request, "_admin/blog/post_form.html", context)

    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug)
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        formset = BlogImageFormSet(request.POST, request.FILES, instance=post)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Blog post updated successfully!")
            return redirect("admin:blog_posts")

        context = {
            "form": form,
            "formset": formset,
            "post": post,
            "title": f"Edit: {post.title}",
        }
        return render(request, "_admin/blog/post_form.html", context)


class BlogPostDeleteView(AdminRequiredMixin, View):
    """Delete blog post"""

    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug)
        post.delete()
        messages.success(request, "Blog post deleted successfully!")
        return redirect("admin:blog_posts")


class BlogCommentListView(AdminRequiredMixin, ListView):
    """Admin comment management"""

    model = Comment
    template_name = "_admin/blog/comment_list.html"
    context_object_name = "comments"
    paginate_by = 20

    def get_queryset(self):
        queryset = Comment.objects.all().select_related("post", "author")
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_status"] = self.request.GET.get("status")
        return context


class BlogCommentActionView(AdminRequiredMixin, View):
    """Approve/reject comments"""

    def post(self, request, comment_id, action):
        comment = get_object_or_404(Comment, id=comment_id)

        if action == "approve":
            comment.status = "approved"
            messages.success(request, "Comment approved!")
        elif action == "reject":
            comment.status = "rejected"
            messages.success(request, "Comment rejected!")

        comment.save()
        return redirect("admin:blog_comments")


class BlogCategoryListView(AdminRequiredMixin, ListView):
    """Manage blog categories"""

    model = Category
    template_name = "_admin/blog/categories.html"
    context_object_name = "categories"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CategoryForm()
        return context

    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect("admin:blog_categories")

        context = {
            "categories": Category.objects.all(),
            "form": form,
        }
        return render(request, "_admin/blog/categories.html", context)


class BlogTagListView(AdminRequiredMixin, ListView):
    """Manage blog tags"""

    model = Tag
    template_name = "_admin/blog/tags.html"
    context_object_name = "tags"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = TagForm()
        return context

    def post(self, request):
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag created successfully!")
            return redirect("admin:blog_tags")

        context = {
            "tags": Tag.objects.all(),
            "form": form,
        }
        return render(request, "_admin/blog/tags.html", context)


# Gallery Management Views
class GalleryDashboardView(AdminRequiredMixin, ListView):
    model = GalleryFolder
    template_name = "_admin/gallery/dashboard.html"
    context_object_name = "folders"
    paginate_by = 12

    def get_queryset(self):
        return GalleryFolder.objects.all().order_by('order', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_folders"] = GalleryFolder.objects.count()
        context["total_images"] = GalleryImage.objects.count()
        context["total_videos"] = GalleryVideo.objects.count()
        context["active_folders"] = GalleryFolder.objects.filter(is_active=True).count()
        context["active_images"] = GalleryImage.objects.filter(is_active=True).count()
        context["active_videos"] = GalleryVideo.objects.filter(is_active=True).count()
        return context


class GalleryFolderCreateView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        order = request.POST.get("order", 0)
        is_active = request.POST.get("is_active") == "on"

        if name:
            try:
                folder = GalleryFolder.objects.create(
                    name=name,
                    description=description,
                    order=int(order) if order else 0,
                    is_active=is_active
                )
                messages.success(request, f"Gallery folder '{folder.name}' created successfully!")
            except Exception as e:
                messages.error(request, f"Error creating folder: {str(e)}")
        else:
            messages.error(request, "Folder name is required.")

        return redirect("admin:gallery_dashboard")


class GalleryFolderUpdateView(AdminRequiredMixin, View):
    def post(self, request, folder_id, *args, **kwargs):
        folder = get_object_or_404(GalleryFolder, id=folder_id)
        
        folder.name = request.POST.get("name", folder.name)
        folder.description = request.POST.get("description", folder.description)
        folder.order = int(request.POST.get("order", folder.order))
        folder.is_active = request.POST.get("is_active") == "on"
        
        try:
            folder.save()
            messages.success(request, f"Folder '{folder.name}' updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating folder: {str(e)}")
        
        return redirect("admin:gallery_dashboard")


class GalleryFolderDeleteView(AdminRequiredMixin, View):
    def post(self, request, folder_id, *args, **kwargs):
        folder = get_object_or_404(GalleryFolder, id=folder_id)
        folder_name = folder.name
        
        try:
            folder.delete()
            messages.success(request, f"Folder '{folder_name}' deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting folder: {str(e)}")
        
        return redirect("admin:gallery_dashboard")


class GalleryImageUploadView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        folder_id = request.POST.get("folder")
        title = request.POST.get("title", "")
        alt_text = request.POST.get("alt_text", "")
        order = request.POST.get("order", 0)
        uploaded_files = request.FILES.getlist("images")

        folder = get_object_or_404(GalleryFolder, id=folder_id)
        
        success_count = 0
        error_count = 0

        for file in uploaded_files:
            try:
                image = GalleryImage.objects.create(
                    folder=folder,
                    title=title or f"Image in {folder.name}",
                    image=file,
                    alt_text=alt_text or title or f"Image in {folder.name}",
                    order=int(order) if order else 0,
                    uploaded_by=request.user.get_full_name() or request.user.email
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error uploading {file.name}: {str(e)}")

        if success_count > 0:
            messages.success(request, f"Successfully uploaded {success_count} image(s) to '{folder.name}'!")
        
        if error_count > 0:
            messages.error(request, f"Failed to upload {error_count} image(s).")

        return redirect("admin:gallery_dashboard")


class GalleryVideoUploadView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        folder_id = request.POST.get("folder")
        title = request.POST.get("title", "")
        order = request.POST.get("order", 0)
        uploaded_files = request.FILES.getlist("videos")
        
        # Handle thumbnail upload
        thumbnail = request.FILES.get("thumbnail")

        folder = get_object_or_404(GalleryFolder, id=folder_id)
        
        success_count = 0
        error_count = 0

        for file in uploaded_files:
            try:
                # Get file size
                file_size = file.size if hasattr(file, 'size') else None
                
                video = GalleryVideo.objects.create(
                    folder=folder,
                    title=title or f"Video in {folder.name}",
                    video=file,
                    thumbnail=thumbnail,
                    file_size=file_size,
                    order=int(order) if order else 0,
                    uploaded_by=request.user.get_full_name() or request.user.email
                )
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error uploading {file.name}: {str(e)}")

        if success_count > 0:
            messages.success(request, f"Successfully uploaded {success_count} video(s) to '{folder.name}'!")
        
        if error_count > 0:
            messages.error(request, f"Failed to upload {error_count} video(s).")

        return redirect("admin:gallery_dashboard")


class GalleryVideoDeleteView(AdminRequiredMixin, View):
    def post(self, request, video_id, *args, **kwargs):
        video = get_object_or_404(GalleryVideo, id=video_id)
        folder_name = video.folder.name
        folder_id = video.folder.id
        
        try:
            video.delete()
            messages.success(request, f"Video deleted from '{folder_name}' successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting video: {str(e)}")
        
        # Check if we came from folder detail view
        if 'folder_detail' in request.META.get('HTTP_REFERER', ''):
            return redirect("admin:gallery_folder_detail", folder_id=folder_id)
        else:
            return redirect("admin:gallery_dashboard")


class GalleryVideoUpdateView(AdminRequiredMixin, View):
    def post(self, request, video_id, *args, **kwargs):
        video = get_object_or_404(GalleryVideo, id=video_id)
        
        # Update video fields
        video.title = request.POST.get("title", video.title)
        video.order = int(request.POST.get("order", video.order))
        video.is_active = request.POST.get("is_active") == "on"
        
        # Handle thumbnail update if provided
        if 'thumbnail' in request.FILES:
            video.thumbnail = request.FILES['thumbnail']
        
        try:
            video.save()
            messages.success(request, f"Video updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating video: {str(e)}")
        
        return redirect("admin:gallery_folder_detail", folder_id=video.folder.id)


class GalleryImageDeleteView(AdminRequiredMixin, View):
    def post(self, request, image_id, *args, **kwargs):
        image = get_object_or_404(GalleryImage, id=image_id)
        folder_name = image.folder.name
        folder_id = image.folder.id
        
        try:
            image.delete()
            messages.success(request, f"Image deleted from '{folder_name}' successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting image: {str(e)}")
        
        # Check if we came from folder detail view
        if 'folder_detail' in request.META.get('HTTP_REFERER', ''):
            return redirect("admin:gallery_folder_detail", folder_id=folder_id)
        else:
            return redirect("admin:gallery_dashboard")


class GalleryFolderDetailView(AdminRequiredMixin, TemplateView):
    template_name = "_admin/gallery/folder_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_id = kwargs['folder_id']
        folder = get_object_or_404(GalleryFolder, id=folder_id)
        
        # Get images and videos ordered by order field, then created_at
        images = folder.images.all().order_by('order', 'created_at')
        videos = folder.videos.all().order_by('order', 'created_at')
        
        # Get mixed media for display
        mixed_media = folder.get_latest_media(limit=None)  # Get all media
        
        context.update({
            'folder': folder,
            'images': images,
            'videos': videos,
            'mixed_media': mixed_media,
            'total_images': images.count(),
            'total_videos': videos.count(),
            'total_media': images.count() + videos.count(),
            'active_images': images.filter(is_active=True).count(),
            'active_videos': videos.filter(is_active=True).count(),
        })
        return context


class GalleryImageUpdateView(AdminRequiredMixin, View):
    def post(self, request, image_id, *args, **kwargs):
        image = get_object_or_404(GalleryImage, id=image_id)
        
        # Update image fields
        image.title = request.POST.get("title", image.title)
        image.alt_text = request.POST.get("alt_text", image.alt_text)
        image.order = int(request.POST.get("order", image.order))
        image.is_active = request.POST.get("is_active") == "on"
        
        try:
            image.save()
            messages.success(request, f"Image updated successfully!")
        except Exception as e:
            messages.error(request, f"Error updating image: {str(e)}")
        
        return redirect("admin:gallery_folder_detail", folder_id=image.folder.id)


class GalleryBulkImageOrderView(AdminRequiredMixin, View):
    def post(self, request, folder_id, *args, **kwargs):
        folder = get_object_or_404(GalleryFolder, id=folder_id)
        
        # Get the new order data from the request
        image_orders = request.POST.getlist('image_orders')
        
        success_count = 0
        error_count = 0
        
        for order_data in image_orders:
            try:
                image_id, new_order = order_data.split(':')
                image = GalleryImage.objects.get(id=image_id, folder=folder)
                image.order = int(new_order)
                image.save()
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error updating order for image {image_id}: {str(e)}")
        
        if success_count > 0:
            messages.success(request, f"Successfully updated order for {success_count} image(s)!")
        
        if error_count > 0:
            messages.error(request, f"Failed to update {error_count} image(s).")
        
        return redirect("admin:gallery_folder_detail", folder_id=folder_id)
