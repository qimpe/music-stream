from django.urls import path

from .views import TrackStream

app_name = "stream_track"


urlpatterns = [
    path("stream/track/<int:track_id>/", TrackStream.as_view(), name="stream_track"),
]
