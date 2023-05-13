import pytest

from accounts.forms import UserRegistrationForm


# pylint: disable=missing-function-docstring


@pytest.mark.django_db
def test_user_registration_form_is_valid():
    form = UserRegistrationForm(
        data={
            "username": "FormTest",
            "first_name": "User",
            "last_name": "Name",
            "email": "name@email.com",
            "password1": "3rq3r25g",
            "password2": "3rq3r25g",
        }
    )
    assert form.is_valid()


@pytest.mark.django_db
def test_user_registration_form_is_invalid():
    form = UserRegistrationForm(
        data={
            "username": "FormTest",
            "first_name": "",
            "last_name": "",
            "email": "name@email.com",
            "password1": "3rq3r25g",
            "password2": "3rq3r25g",
        }
    )
    assert not form.is_valid()
