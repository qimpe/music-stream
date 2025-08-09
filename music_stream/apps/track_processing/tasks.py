from celery import shared_task

from apps.music.models import Track
from .services import TrackConvertorHLS


@shared_task
def process_track(track_id: int) -> None:
    """Обработка трека в hls пригодный формат."""
    track = Track.objects.get(id=track_id)
    track_service = TrackConvertorHLS()
    track_service.convert_track(track.pk)
    print(f"Processing track: {track.title}")
