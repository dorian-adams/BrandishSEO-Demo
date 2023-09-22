from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from brandishseo.cdn.backends import MediaStorage


def directory_path(instance, filename):
    """
    Creates a path to upload a user's profile image.
    :param instance: UserProfile instance
    :param filename: Image file name
    :return: directory path as profiles/{user}/{filename}
    """
    return f"profiles/{instance.user.username}/{filename}"


class User(AbstractUser):
    """
    Default User model.
    """

    initials = models.CharField(max_length=2)

    def save(self, *args, **kwargs):
        if self.initials == "":
            self.initials = (
                self.first_name[:1].upper() + self.last_name[:1].upper()
            )
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Abstract model that sets fields shared between ``AuthorProfile`` and ``CustomerProfile``.
    """

    class Meta:
        abstract = True

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    profile_image = models.ImageField(
        upload_to=directory_path, storage=MediaStorage(), blank=True, null=True
    )
