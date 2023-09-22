"""
brandishseo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

from .base_settings import SETTINGS_FILE

urlpatterns = [
    path("blog/", include(wagtail_urls)),
    path("admin/", admin.site.urls),
    path("cms/", include(wagtailadmin_urls)),
    path("free-seo-tool/", include("seotools.freetools.urls")),
    path("checkout/", include("checkout.urls")),
    path("project/", include("projects.urls")),
    path("account/", include("accounts.urls")),
    path("", include("core.urls")),
]

if SETTINGS_FILE == "brandishseo.local_settings":
    urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))
