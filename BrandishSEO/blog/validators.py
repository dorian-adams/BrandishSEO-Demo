"""
Model field validators.
"""

from django.core.exceptions import ValidationError


def validate_twitter_handle(handle):
    """
    Ensure Twitter handle starts with an '@' symbol.
    :param handle: ``AuthorProfile.twitter_handle``
    """
    if handle[0] != "@":
        raise ValidationError("Handle must start with '@'")
