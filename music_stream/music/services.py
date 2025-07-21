from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import QuerySet
from django.http.request import HttpRequest

from .forms import ArtistCreateForm
from .models import Artist, UserArtist


def create_artist(request: HttpRequest, form: ArtistCreateForm) -> Artist | None:
    """Создает артиста."""
    artist = form.save(commit=False)
    if isinstance(artist, Artist):
        with transaction.atomic():
            artist.save()
            create_user_artist(request.user, artist)  # type: ignore
            return artist
    return None


def create_user_artist(user: User, artist: Artist) -> UserArtist:
    """Привязывает к пользователю артиста и возвращает объект."""
    return UserArtist.objects.create(user=user, artist=artist)


def fetch_artist_queryset_by_slug(slug: str) -> QuerySet[Artist]:
    """Возвращает queryset артиста по slug, если не найден то возвращает пустой queryset."""
    return Artist.objects.filter(slug=slug) or Artist.objects.none()
