"""
Configuration for DO Spaces AWS S3 storage.
Handles media files.
"""

import os

AWS_ACCESS_KEY_ID = os.environ.get("CDN_ACCESS")
AWS_SECRET_ACCESS_KEY = os.environ.get("CDN_SECRET")
AWS_STORAGE_BUCKET_NAME = "brandishseo"
AWS_S3_ENDPOINT_URL = "https://nyc3.digitaloceanspaces.com"
AWS_LOCATION = f"https://{AWS_STORAGE_BUCKET_NAME}.nyc3.digitaloceanspaces.com"
DEFAULT_FILE_STORAGE = "brandishseo.cdn.backends.MediaStorage"
