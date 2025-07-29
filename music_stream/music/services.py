import typing

import mutagen
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import QuerySet, Sum
from django.http.request import HttpRequest

from .forms import AlbumForm, ArtistCreateForm
from .models import (
    Album,
    AlbumArtist,
    AlbumGenres,
    Artist,
    ArtistTrack,
    Genre,
    Status,
    Track,
    TrackInAlbum,
    TrackMetadata,
)


class ArtistService:
    """Сервис для модели: Artist."""

    def create_artist(self, request: HttpRequest, form: ArtistCreateForm) -> Artist:
        """Создает артиста или вызывает исключение при ошибке."""
        with transaction.atomic():
            form.full_clean()
            artist = form.save(commit=False)
            artist.user = request.user
            artist.save()
            return artist

    def fetch_artist_queryset_by_id(self, artist_id: int) -> QuerySet[Artist]:
        """Возвращает queryset артиста по его id, если не найден то возвращает пустой queryset."""
        return Artist.objects.filter(id=artist_id)

    def fetch_all_artist_releases(self, artist_id: int) -> QuerySet[Track | Album]:
        """Возвращает релизы все релизы артиста и сортирует по недавним."""
        album_service = AlbumArtistService()
        artist_track_service = ArtistTrackService()
        albums = album_service.fetch_artist_albums(artist_id)
        artist_track_service.fetch_artist_tracks(artist_id)
        # chain(albums.order_by("release_date"), tracks.order_by("release_date"))
        return albums

    def fetch_artist_by_user_id(self, user_id: int) -> Artist | None:
        """Возвращает артиста по id пользователя или возвращает None."""
        return Artist.objects.filter(user_id=user_id).first()

    def is_user_has_artist(self, user_id: int) -> bool:
        """проверяет есть ли у пользователя артист."""
        return Artist.objects.filter(user_id=user_id).exists()


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


class AlbumArtistService:
    """Сервис для модели: AlbumArtist."""

    def create_artist_album(self, artist: Artist, album: Album) -> None:
        """Привязывает альбом к артисту."""
        AlbumArtist.objects.create(artist=artist, album=album)

    def fetch_artist_albums(self, artist_id: int) -> QuerySet[AlbumArtist]:
        """Возвращает все альбомы артиста по его id и загужает объекты альбомов."""
        return AlbumArtist.objects.filter(artist_id=artist_id)


class TrackService:
    """Сервис для модели: Track."""

    def create_metadata_for_tracks_list(self, tracks_list: list[Track]) -> None:
        """Создает метаданные для списка треков и возвращает объекты TrackMetadata."""
        tracks_metadata = []
        for track in tracks_list:
            metadata = self.create_track_metadata(track)
            if metadata:
                # Создаем объект TrackMetadata и добавляем в список
                track_meta = TrackMetadata(
                    track=track,
                    duration=metadata.get("duration", 0),
                    file_size=metadata.get("size", 0),
                    bitrate=metadata.get("bitrate", 0),
                )
                tracks_metadata.append(track_meta)
        TrackMetadata.objects.bulk_create(tracks_metadata)

    def create_track_metadata(self, track: Track) -> dict[str, typing.Any] | None:
        """Создает метадату для трека и возвращает словарь."""
        try:
            file_path = track.audio_file.path
            metadata = {"size": track.audio_file.size}  # Размер всегда доступен

            with default_storage.open(file_path, "rb") as f:
                audio = mutagen.File(f, easy=True)
                if not audio:
                    return metadata  # Возвращаем хотя бы размер

                if hasattr(audio.info, "length"):
                    metadata["duration"] = audio.info.length

                bitrate = None
                if hasattr(audio.info, "bitrate"):
                    bitrate = audio.info.bitrate
                elif hasattr(audio.info, "sample_rate") and hasattr(audio.info, "bits_per_sample"):
                    channels = getattr(audio.info, "channels", 1)
                    bitrate = audio.info.sample_rate * audio.info.bits_per_sample * channels

                if bitrate:
                    metadata["bitrate"] = bitrate

        except Exception as e:
            print(f"Error processing metadata for track {track.id}: {e}")
            return None
        else:
            return metadata

    def create_track_from_formset(self, track_formset) -> list[tuple[Track, int]]:
        """Создает список треков их позиций в альбоме, данные которых лежат в форме при создании альбома."""
        return [
            (
                Track(
                    title=form.cleaned_data.get("track_title"),
                    is_explicit=form.cleaned_data.get(
                        "is_explicit", False
                    ),  # если is_explicit != True, то передает False по дефолту
                    audio_file=form.cleaned_data.get("audio_file"),
                ),
                form.cleaned_data["position"],
            )
            for form in track_formset
        ]


class TrackInAlbumService:
    """Сервис для модели: TrackInAlbum."""

    def add_tracks_in_album(self, track_list: list[tuple], album: Album) -> None:
        """Добавляет трек в альбом вместе с позицией."""
        tracks_in_album = [TrackInAlbum(album=album, track=track, position=position) for track, position in track_list]
        TrackInAlbum.objects.bulk_create(tracks_in_album)

    def fetch_tracks_in_album(self, album_id: int) -> QuerySet[Track]:
        """возвращает все треки в альбоме."""
        track_ids = (
            TrackInAlbum.objects.filter(album_id=album_id).values_list("track_id", flat=True).order_by("position")
        )
        return Track.objects.filter(id__in=track_ids)

    def count_album_length_in_minutes(self, tracks: QuerySet[Track]) -> str:
        """Возвращает длину альбома в минутах в качестве строки."""
        duration_in_seconds = (
            TrackMetadata.objects.filter(track__in=tracks).aggregate(total_duration=Sum("duration"))["total_duration"]
            or 0
        )
        duration = ""
        hour_in_seconds = 3600
        if duration_in_seconds > hour_in_seconds:
            hours = duration_in_seconds // 3600
            duration += f"{hours}"
        minutes = (duration_in_seconds % 3600) // 60
        seconds = duration_in_seconds % 60
        duration += f"{minutes:02d}:{seconds:02d}"
        return duration


class ArtistTrackService:
    """Сервис для модели: ArtistTrack."""

    def fetch_artist_tracks(self, artist_id: int) -> QuerySet[Track]:
        tracks_ids = ArtistTrack.objects.filter(artist_id=artist_id).values_list("track_id", flat=True)
        return Track.objects.filter(id__in=tracks_ids)


class GenreService:
    """Сервис для модели: Genre."""

    def fetch_all_genres_titles(self) -> QuerySet[Genre]:
        """Возвращает название всех жанров."""
        return Genre.objects.all().only("title")

    def fetch_genre_by_title(self, title: str) -> Genre | None:
        """Возвращает объект трека оп его названию."""
        return Genre.objects.filter(title=title).first()


class GenreAlbumService:
    """Сервис для модели: GenreAlbum."""

    def link_genre_with_album(self, album_id: int, genre_id: int) -> AlbumGenres:
        """Связывает альбом и жанр в отдельную модель."""
        return AlbumGenres.objects.create(album_id=album_id, genre_id=genre_id)


class GenreTrackService:
    """Сервис для модели: GenreTrack."""

    def link_genre_with_tracks(self: list) -> None:
        """Связывает трек и жанр в отдельную модель."""
