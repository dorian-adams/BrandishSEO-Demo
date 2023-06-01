from django.urls import path
from . import views
from .views import ContactView

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("about/", views.about, name="about"),
    path("seo-audit-services/", views.services, name="services"),
]
