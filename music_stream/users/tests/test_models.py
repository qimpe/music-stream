import pytest

from .factories import UserFactory


@pytest.mark.django_db
def test_create_user() -> None:
    user = UserFactory()
    assert "@" in user.email
    assert user.username is not None
