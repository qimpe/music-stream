from django.db.models import QuerySet

from apps.music.models import ArtistTrack, Track


class ArtistTrackService:
    """Сервис для модели: ArtistTrack."""

    def fetch_artist_tracks(self, artist_id: int) -> QuerySet[Track]:
        """Получает все треки артиста по его id."""
        tracks_ids = ArtistTrack.objects.filter(artist_id=artist_id).values_list("track_id", flat=True)
        return Track.objects.filter(id__in=tracks_ids)

    def create_artist_track(self, artist_id: int, track_id: int) -> None:
        """Связывает артиста с треком."""
        ArtistTrack.objects.create(artist_id=artist_id, track_id=track_id)
