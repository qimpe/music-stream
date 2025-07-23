import typing

import mutagen
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import QuerySet
from django.http.request import HttpRequest

from .forms import AlbumCreateForm, ArtistCreateForm
from .models import Album, AlbumArtist, Artist, Track, TrackInAlbum, TrackMetadata, UserArtist


class ArtistService:
    """Сервис для модели: Artist."""

    def create_artist(self, request: HttpRequest, form: ArtistCreateForm) -> Artist:
        """Создает артиста или вызывает исключение при ошибке."""
        artist = form.save(commit=False)
        with transaction.atomic():
            artist.save()
            user_artist_service = UserArtistService()
            user_artist_service.create_user_artist(request.user, artist)  # type: ignore
            return artist

    def fetch_artist_queryset_by_id(self, artist_id: int) -> QuerySet[Artist]:
        """Возвращает queryset артиста по его id, если не найден то возвращает пустой queryset."""
        return Artist.objects.filter(id=artist_id)


class UserArtistService:
    """Сервис для модели: UserArtist."""

    def create_user_artist(self, user: User, artist: Artist) -> UserArtist:
        """Привязывает к пользователю артиста и возвращает объект."""
        if UserArtist.objects.filter(user=user, artist=artist).exists():
            msg = "Artist alredy in album"
            raise BadRequest(msg)
        return UserArtist.objects.create(user=user, artist=artist)

    def fetch_artist_by_user_id(self, user_id: int) -> UserArtist | None:
        """Получает артиста по id пользователя."""
        return (
            UserArtist.objects.select_related("artist").filter(user_id=user_id).first()
        )  #! проблема в том что у пользователя может быть больше 1 артиста


class AlbumService:
    """Сервис для модели: Album."""

    def create_album(self, user_id: int, album_form: AlbumCreateForm, track_formset) -> Album:
        """Создает альбом и треки которые в него входят."""
        artist_service = UserArtistService()
        album_artist = AlbumArtistService()
        track_service = TrackService()
        track_in_album = TrackInAlbumService()
        with transaction.atomic():
            users_artist = artist_service.fetch_artist_by_user_id(user_id)
            if not users_artist:
                msg = "Артист не найден для пользователя"
                raise ValueError(msg)
            artist = users_artist.artist
            album = album_form.save()

            tracks_with_positions = track_service.create_track_from_formset(track_formset, artist)
            tracks_data = [track for track, position in tracks_with_positions]
            tracks = Track.objects.bulk_create(tracks_data)

            album_artist.create_artist_album(artist, album)
            track_in_album.add_tracks_in_album(tracks_with_positions, album)
            track_service.create_metadata_for_tracks_list(tracks)
            return album


class AlbumArtistService:
    """Сервис для модели: AlbumArtist."""

    def create_artist_album(self, artist: Artist, album: Album) -> None:
        """Привязывает альбом к артисту."""
        AlbumArtist.objects.create(artist=artist, album=album)

    def fetch_artist_albums(self, artist_id: int) -> QuerySet[AlbumArtist]:
        """Возвращает все альбомы артиста по его id и загужает объекты альбомов."""
        return AlbumArtist.objects.filter(artist_id=artist_id).select_related("album")


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

    def create_track_from_formset(self, track_formset, artist: Artist) -> list[tuple[Track, int]]:
        """Создает список треков их позиций в альбоме, данные которых лежат в форме при создании альбома."""
        return [
            (
                Track(
                    title=form.cleaned_data.get("track_title"),
                    is_explicit=form.cleaned_data.get(
                        "is_explicit", False
                    ),  # если is_explicit != True, то передает False по дефолту
                    audio_file=form.cleaned_data.get("audio_file"),
                    artist=artist,
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
