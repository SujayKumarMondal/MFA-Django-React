from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render

def root_page(request):
    return render(request, "index.html")

urlpatterns = [
    path("", root_page),
    path("admin/", admin.site.urls),
    path("auth/", include("auth_app.urls")),
]
