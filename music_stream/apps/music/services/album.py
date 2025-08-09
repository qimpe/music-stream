from django.core.exceptions import PermissionDenied
from django.db import transaction

from apps.music.forms import AlbumForm
from apps.music.models import Album, Status, Track
from apps.track_processing.tasks import process_track
from .album_artist import AlbumArtistService
from .artist import ArtistService
from .genre import GenreService
from .genre_album import GenreAlbumService
from .genre_track import GenreTrackService
from .track import TrackService
from .track_in_album import TrackInAlbumService


class AlbumService:
    """Сервис для модели: Album."""

    def create_album(self, user_id: int, album_form: AlbumForm, track_formset) -> Album:
        """Создает альбом и треки которые в него входят."""
        artist_service = ArtistService()
        album_artist = AlbumArtistService()
        track_service = TrackService()
        track_in_album = TrackInAlbumService()
        genre_album_service = GenreAlbumService()
        genre_service = GenreService()
        GenreTrackService()
        with transaction.atomic():
            artist = artist_service.fetch_artist_by_user_id(user_id)
            if not artist:
                msg = "Артист не найден для этого пользователя"
                raise ValueError(msg)
            album = album_form.save()
            album_genre_title = album_form.data.get("genre")

            if not album_genre_title:
                return None
            genre = genre_service.fetch_genre_by_title(album_genre_title)
            if genre:
                genre_album_service.link_genre_with_album(album.id, genre.id)
            print(track_formset.data)
            # track_genre_service.create_tracks_genres(track_list)
            tracks_with_positions = track_service.create_track_from_formset(track_formset)
            tracks_data = [track for track, position in tracks_with_positions]
            tracks = Track.objects.bulk_create(tracks_data)
            process_track.delay(tracks[0].pk)
            album_artist.create_artist_album(artist, album)
            track_in_album.add_tracks_in_album(tracks_with_positions, album)
            track_service.create_metadata_for_tracks_list(tracks)
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
