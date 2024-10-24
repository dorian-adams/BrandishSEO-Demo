from django.urls import path

from seotools import views

app_name = "freetools"

urlpatterns = [
    path("", views.seo_tools, name="seo_tools"),
]
