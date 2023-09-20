from django.urls import path

from seotools.freetools import views

app_name = "freetools"

urlpatterns = [
    path("", views.seo_tools, name="seo_tools"),
]
