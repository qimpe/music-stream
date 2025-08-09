import logging
import typing

import mutagen
from django.core.files.storage import default_storage
from django.db import transaction
from django.forms import inlineformset_factory

from apps.music.forms import TrackCreateForm
from apps.music.models import Track, TrackMetadata
from apps.track_processing.tasks import process_track
from .artist import ArtistService
from .artist_track import ArtistTrackService

logger = logging.getLogger(__name__)


class TrackService:
    """Сервис для модели: Track."""

    def __init__(self) -> None:
        self.artist_service = ArtistService()
        self.artist_track_service = ArtistTrackService()

    def create_track(self, user_id: int, form: TrackCreateForm) -> None:
        """Создает трек на основе формы."""
        with transaction.atomic():
            if artist := self.artist_service.fetch_artist_by_user_id(user_id):
                track = form.save()
                self.artist_track_service.create_artist_track(artist.pk, track.id)
                process_track.delay(track.id)

    def create_metadata_for_tracks_list(self, tracks_list: list[Track]) -> None:
        """Создает метаданные для списка треков."""
        tracks_metadata = [
            TrackMetadata(
                track=track,
                duration=metadata.get("duration", 0),
                file_size=metadata.get("size", 0),
                bitrate=metadata.get("bitrate", 0),
            )
            for track in tracks_list
            if (metadata := self.create_track_metadata(track))
        ]
        TrackMetadata.objects.bulk_create(tracks_metadata)

    def create_track_metadata(self, track: Track) -> dict[str, typing.Any] | None:
        """Создает метадату для трека и возвращает словарь с метадатой трека."""
        try:
            track_file_path = track.audio_file.path
            metadata = {"size": track.audio_file.size}

            with default_storage.open(track_file_path, "rb") as f:
                audio = mutagen.File(f, easy=True)
                if not audio:
                    return metadata

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

                return metadata
        except FileNotFoundError as e:
            logger.warning(f"Error creating metadata for track {track.id}: {e}")
            return None

    def create_track_from_formset(self, track_formset: inlineformset_factory) -> list[tuple[Track, int]]:
        """Создает список треков с их позициями в альбоме."""
        return [
            (
                Track(
                    title=form.cleaned_data.get("track_title"),
                    is_explicit=form.cleaned_data.get("is_explicit", False),
                    audio_file=form.cleaned_data.get("audio_file"),
                ),
                form.cleaned_data["position"],
            )
            for form in track_formset
        ]

    def update_hls_playlist_url(self, track_id: int, playlist_url: str) -> None:
        """Обновляет URL HLS-плейлиста трека."""
        Track.objects.filter(id=track_id).update(hls_playlist=playlist_url)

    def fetch_track_by_id(self, track_id: int) -> Track:
        """Возвращает трек по его id в ином случае исключение 'DoesNotExist'."""
        return Track.objects.get(id=track_id)
