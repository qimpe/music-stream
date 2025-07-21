import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.utils.text import slugify

from music.models import Artist, UserArtist
from .factories import ArtistFactory, UserFactory, UsersArtistFactory


@pytest.mark.django_db
def test_create_user() -> None:
    user = UserFactory()
    assert "@" in user.email
    assert user.username is not None


@pytest.mark.django_db
def test_create_artist() -> None:
    artist: Artist = ArtistFactory()
    assert artist.slug == slugify(artist.name)
    assert artist.status == "in_pending"


@pytest.mark.django_db
def test_user_delete_sets_null() -> None:
    artist = ArtistFactory()
    user = UserFactory()
    user_artist = UserArtist.objects.create(user=user, artist=artist)

    user.delete()
    user_artist.refresh_from_db()  # Важно: обновляем объект из БД

    assert user_artist.user is None
    assert UserArtist.objects.count() == 1


@pytest.mark.django_db
def test_artist_delete_cascades() -> None:
    artist = ArtistFactory()
    user = UserFactory()
    user_artist = UserArtist.objects.create(user=user, artist=artist)

    artist.delete()

    assert UserArtist.objects.count() == 0
    # Проверка, что объект больше нельзя обновить
    with pytest.raises(ObjectDoesNotExist):
        user_artist.refresh_from_db()


# Тест 4: Проверка уникальности связи
@pytest.mark.django_db
def test_unique_user_artist() -> None:
    artist = ArtistFactory()
    user = UserFactory()
    UserArtist.objects.create(user=user, artist=artist)

    with pytest.raises(IntegrityError):
        UserArtist.objects.create(user=user, artist=artist)


@pytest.mark.django_db
def test_delete_user_when_artist_is_none() -> None:
    UsersArtistFactory(user=None)
    user = UserFactory()

    # Должно работать без ошибок
    user.delete()
    assert UserArtist.objects.count() == 1
