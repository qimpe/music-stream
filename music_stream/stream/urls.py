from django.urls import path

from . import views

app_name = "stream"
urlpatterns = [
    path("<int:track_id>/", views.stream_track, name="stream"),
]
