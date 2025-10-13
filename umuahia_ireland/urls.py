from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import handler404, handler500
from .errors import custom_error_404, custom_error_500
from .views import send_email, privacy_statement
from django.views.generic import TemplateView
from .media_debug import media_test_view
from .csrf_test_views import csrf_test
from .stripe_views import (
    create_checkout_session,
    stripe_webhook,
)


handler404 = custom_error_404
handler500 = custom_error_500

urlpatterns = [
    path("", include("app.urls", namespace="app")),
    path("send-email/", send_email, name="send_email"),
    path("privacy/", privacy_statement, name="privacy_statement"),
    path("admin/", include("_admin.urls", namespace="admin")),
    path("dashboard/", include("_admin.urls", namespace="admin")),
    path("user-dashboard/", include("dashboard.urls", namespace="user:")),
    path("auth/", include("accounts.urls", namespace="accounts")),
    path("auth/", include("django.contrib.auth.urls")),
    path("blog/", include("blog.urls", namespace="blog")),
    path("debug/media-test/", media_test_view, name="media_test"),
    path("debug/csrf-test/", csrf_test, name="csrf_test"),
    # Stripe Donation URLs
    path(
        "donate/create-session/",
        create_checkout_session,
        name="create_checkout_session",
    ),
    path("stripe/webhook/", stripe_webhook, name="stripe_webhook"),
    path("cookies-policy/", TemplateView.as_view(template_name="cookies_policy.html"), name="cookies_policy"),
]

# Serve media files in development and production
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production, serve media files through the static files system
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
