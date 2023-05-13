import pytest
from accounts.models import User


@pytest.fixture
def create_user(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="TestUser",
        password="Brandish123",
        first_name="Test",
        last_name="User",
        email="test@email.com",
    )
    return user


@pytest.fixture
def auto_login_user(db, client, create_user):
    user = create_user
    client.force_login(user)
    return user, client
