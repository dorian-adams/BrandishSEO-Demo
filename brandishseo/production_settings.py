"""
Settings for production use only.
"""

# pylint: disable=unused-wildcard-import, wildcard-import

import sys

import dj_database_url

from .base_settings import *

DEBUG = False

if len(sys.argv) > 0 and sys.argv[1] != "collectstatic":
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")

    DATABASES = {
        "default": dj_database_url.parse(os.environ.get("DATABASE_URL")),
    }

ALLOWED_HOSTS = ["brandishseo.com", "www.brandishseo.com"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_BROWSER_XSS_FILTER = True

if os.getenv("PRODUCTION_TEST", None) is None:
    # In production environment
    SECURE_SSL_REDIRECT = True
else:
    # In test production environment
    # SECURE_SSL_REDIRECT default is False
    # Must remain False, else it'll break unit tests
    ALLOWED_HOSTS.extend(["testserver", "localhost"])
