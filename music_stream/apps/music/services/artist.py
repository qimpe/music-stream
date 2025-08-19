from itertools import chain

from django.contrib.auth.models import User
from django.db.models import QuerySet

from apps.music.forms import ArtistCreateForm
from apps.music.models import Album, Artist, Track
from .album_artist import AlbumArtistService
from .artist_track import ArtistTrackService


class ArtistService:
    """Сервис для модели: Artist."""

    def create_artist(self, user: User, form: ArtistCreateForm) -> Artist:
        """Создает артиста или вызывает исключение при ошибке."""
        form.full_clean()
        artist = form.save(commit=False)
        artist.user = user
        artist.save()
        return artist

    def fetch_artist_queryset_by_id(self, artist_id: int) -> QuerySet[Artist]:
        """Возвращает queryset(содержит только 1 артиста) артиста по его id, если не найден то возвращает пустой queryset."""
        return Artist.objects.filter(id=artist_id)

    def fetch_all_artist_releases(self, artist_id: int) -> QuerySet[Track | Album]:
        """Возвращает релизы все релизы артиста и сортирует по недавним."""
        album_service = AlbumArtistService()
        artist_track_service = ArtistTrackService()
        albums = album_service.fetch_artist_albums(artist_id)
        tracks = artist_track_service.fetch_artist_tracks(artist_id)
        return chain(albums, tracks)

    def fetch_artist_by_user_id(self, user_id: int) -> Artist | None:
        """Возвращает артиста по id пользователя или возвращает None."""
        return Artist.objects.filter(user_id=user_id).first()

    def is_user_has_artist(self, user_id: int) -> bool:
        """проверяет есть ли у пользователя артист."""
        return Artist.objects.filter(user_id=user_id).exists()
