from django.shortcuts import render
from .settings import APP_NAME


def custom_error_404(request, exception):
    context = {
        "APP_NAME": APP_NAME,
        "status_code": 404,
    }
    context["message"] = "Sorry, the page you are looking for was not found."
    return render(request, "404.html", context, status=404)


def custom_error_500(request):
    context = {
        "APP_NAME": APP_NAME,
        "status_code": 500,
    }
    context["message"] = "An unexpected error occurred. Please try again later."
    return render(request, "500.html", context, status=500)

def custom_error_403(request, exception=None):
    context = {
        "APP_NAME": APP_NAME,
        "status_code": 403,
        "message": "You do not have permission to access this resource."
    }
    return render(request, "403.html", context, status=403)

def custom_error_400(request, exception=None):
    context = {
        "APP_NAME": APP_NAME,
        "status_code": 400,
        "message": "Bad request. Please check your input and try again."
    }
    return render(request, "400.html", context, status=400)
