import pytest

from accounts.models import User, UserProfile

# pylint: disable=missing-function-docstring


def test_user_attributes():
    assert hasattr(User, "initials")


def test_user_initials_field(create_user):
    user = create_user
    expected_initials = "TU"
    assert expected_initials == user.initials


def test_user_profile_attributes():
    assert hasattr(UserProfile, "user")
    assert hasattr(UserProfile, "profile_image")
