import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.utils.text import slugify
from music.models import Artist

from .factories import ArtistFactory, UserFactory


@pytest.mark.django_db
def test_create_user() -> None:
    user = UserFactory()
    assert "@" in user.email
    assert user.username is not None


@pytest.mark.django_db
def test_create_artist() -> None:
    artist: Artist = ArtistFactory()
    assert artist.slug == slugify(artist.name)
    assert artist.status == "created"


