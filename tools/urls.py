from django.urls import path

from . import views

app_name = "tools"

urlpatterns = [
    path("", views.seo_tools, name="seo_tools"),
]
