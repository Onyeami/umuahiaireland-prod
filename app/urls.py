from django.urls import path
from .views import home, gallery_folders, gallery_folder_detail, members_gallery

app_name = "app"

urlpatterns = [
    path("", home, name="home_page"),
    path("gallery/", gallery_folders, name="gallery_folders"),
    path("gallery/<slug:folder_slug>/", gallery_folder_detail, name="gallery_folder_detail"),
    path("members-gallery/", members_gallery, name="members_gallery"),
]
