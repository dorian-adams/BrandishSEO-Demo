from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from brandishseo.cdn.backends import MediaStorage


def directory_path(instance, filename):
    """
    Creates a path to upload a user's profile image.
    :param instance: UserProfile instance
    :param filename: Image file name
    :return: directory path as profiles/{user}/{filename}
    """
    return "profiles/{0}/{1}".format(instance.user.username, filename)


class User(AbstractUser):
    initials = models.CharField(max_length=2)

    def save(self, *args, **kwargs):
        if self.initials is None:
            self.initials = self.first_name[:1].upper() + self.last_name[:1].upper()
        super(User, self).save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(
        upload_to=directory_path, storage=MediaStorage(), blank=True, null=True
    )

    class Meta:
        abstract = True
