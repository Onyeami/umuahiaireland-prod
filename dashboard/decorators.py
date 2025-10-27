from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps


def validation_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect(reverse("accounts:login"))

        # Check if the user is active
        if not request.user.is_active:
            return HttpResponseForbidden("Your account is inactive")

        # Check if the user is verified (custom attribute)
        if not getattr(request.user, "is_verified", False):
            return HttpResponseForbidden("Your account is not verified. Please check your email for verification link.")


        # Check if the user is approved by admin
        if not getattr(request.user, "is_approved", False):
            # If user is verified but not approved, show pending approval page
            if getattr(request.user, "is_verified", False):
                from django.shortcuts import render
                return render(request, "registration/pending_approval.html")
            return HttpResponseForbidden("Your account is pending admin approval. You will be notified once approved.")

        # If all checks pass, call the view function
        return view_func(request, *args, **kwargs)

    return _wrapped_view
