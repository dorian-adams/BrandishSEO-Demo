"""
Settings for local/development only.
Add apps and middleware that are only used in dev.
"""

# pylint: disable=unused-wildcard-import, wildcard-import

from .base_settings import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1"]
INTERNAL_IPS = [
    "127.0.0.1",
]  # Necessary for WagtailSiteFactory

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

INSTALLED_APPS.extend(["debug_toolbar", "django_extensions"])
MIDDLEWARE.insert(4, "debug_toolbar.middleware.DebugToolbarMiddleware")
