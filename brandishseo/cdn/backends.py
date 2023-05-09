"""
https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
"""

from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = "media"
