from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # Public blog URLs
    path("", views.BlogListView.as_view(), name="post_list"),
    path("search/", views.blog_search, name="search"),
    path("category/<slug:slug>/", views.category_posts, name="category_posts"),
    path("tag/<slug:slug>/", views.tag_posts, name="tag_posts"),
    path("post/<slug:slug>/", views.BlogDetailView.as_view(), name="post_detail"),
    path("post/<slug:slug>/comment/", views.add_comment, name="add_comment"),
    # Admin blog URLs
    path("admin/", views.admin_blog_dashboard, name="admin_dashboard"),
    path("admin/posts/", views.admin_post_list, name="admin_post_list"),
    path("admin/posts/create/", views.admin_create_post, name="admin_create_post"),
    path(
        "admin/posts/<slug:slug>/edit/", views.admin_edit_post, name="admin_edit_post"
    ),
    path(
        "admin/posts/<slug:slug>/delete/",
        views.admin_delete_post,
        name="admin_delete_post",
    ),
    path("admin/comments/", views.admin_comment_list, name="admin_comment_list"),
    path(
        "admin/comments/<uuid:comment_id>/<str:action>/",
        views.admin_comment_action,
        name="admin_comment_action",
    ),
    path(
        "admin/categories/",
        views.admin_manage_categories,
        name="admin_manage_categories",
    ),
    path("admin/tags/", views.admin_manage_tags, name="admin_manage_tags"),
    path("admin/media-debug/", views.admin_media_debug, name="admin_media_debug"),
]
