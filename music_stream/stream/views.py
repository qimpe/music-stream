from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from music.models import Track


def stream_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    bucket = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
    key = track.audio_file.name
    print(key)
    internal_path = f"/{bucket}/{key}"
    print(internal_path)
    response = HttpResponse(status=206, content_type="audio/mpeg")
    response["X-Accel-Redirect"] = internal_path
    response["Content-Type"] = "audio/mpeg"  # Настройте в зависимости от типа файла
    response["X-Accel-Buffering"] = "no"
    return response
