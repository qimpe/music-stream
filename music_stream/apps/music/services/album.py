from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from apps.music.forms import AlbumForm
from apps.music.models import Album, Status, Track
from .album_artist import AlbumArtistService
from .artist import ArtistService
from .genre import GenreService
from .genre_album import GenreAlbumService
from .genre_track import GenreTrackService
from .track import TrackService
from .track_in_album import TrackInAlbumService


class AlbumService:
    """Сервис для модели: Album."""

    def __init__(self) -> None:
        self.genre_service = GenreService()
        self.track_service = TrackService()
        self.artist_service = ArtistService()
        self.album_artist = AlbumArtistService()
        self.track_in_album = TrackInAlbumService()
        self.genre_track_service= GenreTrackService()
        self.genre_album_service = GenreAlbumService()

    def create_album(self, user_id: int, album_form: AlbumForm, track_formset) -> Album:
        """Создает альбом и треки которые в него входят."""
        artist = self.artist_service.fetch_artist_by_user_id(user_id)
        if not artist:
                msg = "У пользователя нет такого артиста"
                raise ValidationError(msg)

        with transaction.atomic():
                album = album_form.save()
                album_genre_title = album_form.data.get("genre")
                if not album_genre_title:
                    msg="Не выбран жанр для альбома"
                    raise ValidationError(msg)

                genre = self.genre_service.fetch_genre_by_title(album_genre_title)
                if not genre:
                    msg="Выбранный жанр не найден"
                    raise ValidationError(msg)

                self.genre_album_service.set_genre_for_album(album.id, genre.id)
                tracks_with_positions = self.track_service.create_track_objs_from_formset(track_formset)
                tracks=self.track_service.bulk_create_track(tracks_with_positions)
                self.album_artist.create_artist_album(artist, album)
                self.track_in_album.add_tracks_in_album(tracks_with_positions, album)
                self.track_service.create_metadata_for_tracks_list(tracks)
                return album

    def update_album_status_on_delete(self, album_id: int) -> None:
        """Обновляет статус альбома на *deleted* и статус всех треков которые в него входили."""
        new_status = "deleted"
        with transaction.atomic():
            Track.objects.filter(trackinalbum__album_id=album_id).update(status=new_status)
            Album.objects.filter(id=album_id).update(status=new_status)

    def delete_album(self, album_id: int) -> None:
        """Удаляет альбом и все треки которые в него входили."""
        with transaction.atomic():
            Track.objects.filter(trackinalbum__album_id=album_id).delete()
            Album.objects.filter(id=album_id).delete()

    def fetch_album_by_id(self, album_id: int) -> Album:
        """Возвращает альбом по его id, в ином случае вызывает исключение."""
        return Album.objects.get(id=album_id)

    def fetch_album_for_update(self, album_id: int) -> Album:
        """Возвращает альбом по его id, в ином случае вызывает исключение."""
        album = self.fetch_album_by_id(album_id)
        if album.status == Status.ACTIVE:
            msg = "Активный альбом нельзя редактировать"
            raise PermissionDenied(msg)
        return album
