from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("about/", views.about, name="about"),
    path("seo-audit-services/", views.services, name="services"),
    path("privacy-policy", views.privacy_policy, name="privacy_policy"),
    path("terms-of-service", views.terms_of_service, name="terms_of_service"),
]
