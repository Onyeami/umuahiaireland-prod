from django.urls import path
from .views import (
    DashboardView,
    ProjectListView,
    MemberListView,
    ProjectListView,
    UserCreateView,
    UserUpdateView,
    UserDeactivateView,
    UserActivateView,
    UserDeleteView,
    UserApproveView,
    UserRejectView,
    MinuitesListView,
    CreateMinuitesView,
    SettingsView,
    ChangePasswordView,
    AdminResetUserPasswordView,
    EditMinuitesView,
    DeleteMinuitesView,
    CreateFinancialCheckbookView,
    EditFinancialCheckbookView,
    DeleteFinancialCheckbookView,
    FinancialCheckbookListView,
    # Blog views
    BlogDashboardView,
    BlogPostListView,
    BlogPostCreateView,
    BlogPostEditView,
    BlogPostDeleteView,
    BlogCommentListView,
    BlogCommentActionView,
    BlogCategoryListView,
    BlogTagListView,
    # Gallery views
    GalleryDashboardView,
    GalleryFolderCreateView,
    GalleryFolderUpdateView,
    GalleryFolderDeleteView,
    GalleryImageUploadView,
    GalleryImageDeleteView,
    GalleryVideoUploadView,
    GalleryVideoDeleteView,
    GalleryVideoUpdateView,
    GalleryFolderDetailView,
    GalleryImageUpdateView,
    GalleryBulkImageOrderView,
)
from app.debug_views import debug_cloudinary_config

app_name = "admin"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("members/", MemberListView.as_view(), name="members"),
    path("create-user/", UserCreateView.as_view(), name="create_user"),
    path(
        "user/<uuid:user_id>/deactivate/",
        UserDeactivateView.as_view(),
        name="deactivate_user",
    ),
    path(
        "user/<uuid:user_id>/activate/",
        UserActivateView.as_view(),
        name="activate_user",
    ),
    path("user/<uuid:user_id>/delete/", UserDeleteView.as_view(), name="delete_user"),
    path(
        "user/<uuid:user_id>/approve/",
        UserApproveView.as_view(),
        name="approve_user",
    ),
    path(
        "user/<uuid:user_id>/reject/",
        UserRejectView.as_view(),
        name="reject_user",
    ),
    path(
        "user/<uuid:user_id>/reset-password/",
        AdminResetUserPasswordView.as_view(),
        name="reset_user_password",
    ),
    path("user/<uuid:user_id>/edit/", UserUpdateView.as_view(), name="edit_user"),
    path("minuites/", MinuitesListView.as_view(), name="minuites"),
    path("create-minuites/", CreateMinuitesView.as_view(), name="create_minutes"),
    path(
        "minuites/<uuid:minuites_id>/edit/",
        EditMinuitesView.as_view(),
        name="edit_minuites",
    ),
    path(
        "minuites/<uuid:minuites_id>/delete/",
        DeleteMinuitesView.as_view(),
        name="delete_minuites",
    ),
    path(
        "checkbook/", FinancialCheckbookListView.as_view(), name="financial_checkbook"
    ),
    path(
        "create-checkbook/",
        CreateFinancialCheckbookView.as_view(),
        name="create_checkbook",
    ),
    path(
        "checkbook/<uuid:checkbook_id>/edit/",
        EditFinancialCheckbookView.as_view(),
        name="edit_checkbook",
    ),
    path(
        "checkbook/<uuid:checkbook_id>/delete/",
        DeleteFinancialCheckbookView.as_view(),
        name="delete_checkbook",
    ),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    # Blog URLs
    path("blog/", BlogDashboardView.as_view(), name="blog_dashboard"),
    path("blog/posts/", BlogPostListView.as_view(), name="blog_posts"),
    path("blog/posts/create/", BlogPostCreateView.as_view(), name="blog_create_post"),
    path(
        "blog/posts/<slug:slug>/edit/",
        BlogPostEditView.as_view(),
        name="blog_edit_post",
    ),
    path(
        "blog/posts/<slug:slug>/delete/",
        BlogPostDeleteView.as_view(),
        name="blog_delete_post",
    ),
    path("blog/comments/", BlogCommentListView.as_view(), name="blog_comments"),
    path(
        "blog/comments/<uuid:comment_id>/<str:action>/",
        BlogCommentActionView.as_view(),
        name="blog_comment_action",
    ),
    path("blog/categories/", BlogCategoryListView.as_view(), name="blog_categories"),
    path("blog/tags/", BlogTagListView.as_view(), name="blog_tags"),
    
    # Gallery URLs
    path("gallery/", GalleryDashboardView.as_view(), name="gallery_dashboard"),
    path("gallery/create-folder/", GalleryFolderCreateView.as_view(), name="gallery_create_folder"),
    path("gallery/folder/<uuid:folder_id>/", GalleryFolderDetailView.as_view(), name="gallery_folder_detail"),
    path("gallery/folder/<uuid:folder_id>/edit/", GalleryFolderUpdateView.as_view(), name="gallery_edit_folder"),
    path("gallery/folder/<uuid:folder_id>/delete/", GalleryFolderDeleteView.as_view(), name="gallery_delete_folder"),
    path("gallery/folder/<uuid:folder_id>/bulk-order/", GalleryBulkImageOrderView.as_view(), name="gallery_bulk_order"),
    path("gallery/upload-images/", GalleryImageUploadView.as_view(), name="gallery_upload_images"),
    path("gallery/upload-videos/", GalleryVideoUploadView.as_view(), name="gallery_upload_videos"),
    path("gallery/image/<uuid:image_id>/edit/", GalleryImageUpdateView.as_view(), name="gallery_edit_image"),
    path("gallery/image/<uuid:image_id>/delete/", GalleryImageDeleteView.as_view(), name="gallery_delete_image"),
    path("gallery/video/<uuid:video_id>/edit/", GalleryVideoUpdateView.as_view(), name="gallery_edit_video"),
    path("gallery/video/<uuid:video_id>/delete/", GalleryVideoDeleteView.as_view(), name="gallery_delete_video"),
    
    # Debug URL (admin only)
    path("debug/cloudinary/", debug_cloudinary_config, name="debug_cloudinary"),
]
