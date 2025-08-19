from django.db.models import QuerySet

from apps.music.models import Album, Track, TrackInAlbum


class TrackInAlbumService:
    """Сервис для модели: TrackInAlbum."""

    def add_tracks_in_album(self, track_list: list[tuple], album: Album) -> None:
        """Добавляет трек в альбом вместе с позицией."""
        TrackInAlbum.objects.bulk_create(
            [TrackInAlbum(album=album, track=track, position=position) for track, position in track_list]
        )

    def fetch_tracks_in_album(self, album_id: int) -> QuerySet[Track]:
        """возвращает все треки в альбоме по id альбома."""
        return (
            Track.objects.filter(track_album__album_id=album_id)
            .select_related("metadata")
            .order_by("track_album__position")
            .distinct()
        )

    """def count_album_length_in_minutes(self, tracks: QuerySet[Track]) -> str:
        Возвращает длину альбома в минутах в качестве строки.
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
"""
