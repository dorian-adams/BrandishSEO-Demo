import pytest
from django.urls import reverse


# pylint: disable=missing-function-docstring


@pytest.mark.django_db
def test_register_user_view_get(client):
    response = client.get(reverse("accounts:register"))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_register_user_view_post(client, django_user_model):
    response = client.post(
        reverse("accounts:register"),
        data={
            "username": "PostTest",
            "first_name": "User",
            "last_name": "Name",
            "email": "user@email.com",
            "password1": "zxceefF1238",
            "password2": "zxceefF1238",
        },
        follow=True,
    )

    assert 200 == response.status_code
    assert django_user_model.objects.count() == 1


def test_user_update_view_get(auto_login_user):
    user, client = auto_login_user
    response = client.get(reverse("accounts:user_update", kwargs={"pk": user.pk}))

    assert 200 == response.status_code
    # Ensure form fields are prepopulated with the user's data.
    assert user.first_name in str(response.content)
    assert user.last_name in str(response.content)
    assert user.email in str(response.content)


@pytest.mark.django_db
def test_user_update_view_post(auto_login_user):
    user, client = auto_login_user
    new_first, new_last, new_email = ("NewFirst", "NewLast", "new@mail.com")
    response = client.post(
        reverse("accounts:user_update", kwargs={"pk": user.pk}),
        data={
            "first_name": new_first,
            "last_name": new_last,
            "email": new_email,
        },
        follow=True,
    )
    user.refresh_from_db()

    assert response.status_code == 200
    assert user.first_name == new_first
    assert user.last_name == new_last
    assert user.email == new_email


def test_update_password_view_get(auto_login_user):
    _, client = auto_login_user
    response = client.get(reverse("accounts:update_password"))
    assert 200 == response.status_code


@pytest.mark.django_db
def test_update_password_view_post(auto_login_user):
    user, client = auto_login_user
    new_password = "47425rhjlkw1259"
    response = client.post(
        reverse("accounts:update_password"),
        data={
            "old_password": "Brandish123",
            "new_password1": new_password,
            "new_password2": new_password,
        },
        follow=True,
    )
    user.refresh_from_db()

    assert 200 == response.status_code
    assert "Password updated successfully." in str(response.content)
    assert user.check_password(new_password)


def test_reset_password_view_get(auto_login_user):
    _, client = auto_login_user
    response = client.get(reverse("accounts:reset_password"))
    assert 200 == response.status_code


def test_reset_password_view_post(auto_login_user, mailoutbox):
    user, client = auto_login_user
    response = client.post(
        reverse("accounts:reset_password"), data={"email": user.email}, follow=True
    )

    assert 200 == response.status_code
    assert "Instructions to reset your password" in str(response.content)
    assert len(mailoutbox) == 1  # Password reset email


def test_profile_view_without_orders(auto_login_user):
    user, client = auto_login_user
    response = client.get(reverse("accounts:profile"))
    assert "Click here to get started" in str(response.content)
    assert user.first_name in str(response.content)


# TODO: Create factories for proper implementation
def test_profile_view_with_order():
    pass
