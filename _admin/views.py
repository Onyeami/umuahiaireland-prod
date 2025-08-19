from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q, Count
from users.models import CustomUser
from app.models import Minuites, FinancialCheckbook
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


class MemberListView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = "_admin/members.html"
    context_object_name = "users"

    def get_queryset(self):
        return CustomUser.objects.all().order_by("-date_joined")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_users"] = self.get_queryset().count()
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
