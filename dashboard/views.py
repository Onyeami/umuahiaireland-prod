from django.shortcuts import render, redirect, get_object_or_404
from .decorators import validation_required
from django.urls import reverse
from users.models import CustomUser
from django.contrib import messages
from app.models import Minuites, FinancialCheckbook
from django.http import HttpResponse
import os


@validation_required
def dashboard(request):
    return render(request, "_user/profile.html")


def minuites(request):
    minutes_list = Minuites.objects.all()

    if request.method == "POST" and "download_minute" in request.POST:
        minute_id = request.POST.get("minute_id")
        minute = get_object_or_404(Minuites, id=minute_id)

        # Return the uploaded file instead of generating a new PDF
        if minute.minuites:
            try:
                # Open and read the file content
                with minute.minuites.open("rb") as file:
                    file_content = file.read()

                # Determine the content type based on file extension
                file_name = minute.minuites.name
                if file_name.lower().endswith(".pdf"):
                    content_type = "application/pdf"
                elif file_name.lower().endswith((".doc", ".docx")):
                    content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                else:
                    content_type = "application/octet-stream"

                response = HttpResponse(file_content, content_type=content_type)
                response["Content-Disposition"] = (
                    f'attachment; filename="{file_name.split("/")[-1]}"'
                )
                return response
            except Exception as e:
                messages.error(request, f"Error downloading file: {str(e)}")
                return redirect("user:minuites")
        else:
            messages.error(request, "No file available for download.")
            return redirect("user:minuites")

    return render(request, "_user/minuites.html", {"minutes": minutes_list})


def checkbooks(request):
    checkbook_list = FinancialCheckbook.objects.all()

    if request.method == "POST" and "download_checkbook" in request.POST:
        checkbook_id = request.POST.get("checkbook_id")
        checkbook = get_object_or_404(FinancialCheckbook, id=checkbook_id)

        # Return the uploaded checkbook file
        if checkbook.checkbook:
            try:
                # Open and read the file content
                with checkbook.checkbook.open("rb") as file:
                    file_content = file.read()

                # Determine the content type based on file extension
                file_name = checkbook.checkbook.name
                if file_name.lower().endswith(".pdf"):
                    content_type = "application/pdf"
                elif file_name.lower().endswith((".doc", ".docx")):
                    content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                elif file_name.lower().endswith((".xls", ".xlsx")):
                    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                else:
                    content_type = "application/octet-stream"

                response = HttpResponse(file_content, content_type=content_type)
                response["Content-Disposition"] = (
                    f'attachment; filename="{file_name.split("/")[-1]}"'
                )
                return response
            except Exception as e:
                messages.error(request, f"Error downloading file: {str(e)}")
                return redirect("user:checkbooks")
        else:
            messages.error(request, "No file available for download.")
            return redirect("user:checkbooks")

    return render(request, "_user/checkbooks.html", {"checkbooks": checkbook_list})


@validation_required
def settings(request):
    return render(request, "_user/settings.html")


@validation_required
def update_profile(request):
    if request.method == "POST":
        # Handle form submission
        first_name = request.POST.get("fullName").split()[0]
        last_name = request.POST.get("fullName").split()[-1]
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        location = request.POST.get("location")
        about = request.POST.get("about")

        # Save changes to the user profile
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone
        user.location = location
        user.about = about
        user.save()

        return redirect(reverse("user:dashboard"))

    return render(request, "_user/update-profile.html")


@validation_required
def change_password(request):
    if request.method == "POST":
        currentPassword = request.POST.get("current-password")
        newPassword = request.POST.get("new-password")
        confirmPassword = request.POST.get("new-password2")

        user = CustomUser.objects.get(id=request.user.id)

        if not user.check_password(currentPassword):
            messages.error(request, "Current password is incorrect!")
            return redirect(reverse("user:settings"))

        if not newPassword == confirmPassword:
            messages.error(request, "Passwords do not match!")
            return redirect(reverse("user:settings"))

        if newPassword == currentPassword:
            messages.error(request, "The new password cannot be your current password!")
            return redirect(reverse("user:settings"))

        user.set_password(newPassword)
        user.save()

        messages.success(
            request,
            "Your password has been changed! You will be redirected to login again",
        )
        return redirect(reverse("user:settings"))
