from django.urls import path

from . import views

app_name = "music"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("create-artist/", views.ArtistCreateView.as_view(), name="create_artist"),
    path("artist/<int:artist_id>/", views.ArtistDetailView.as_view(), name="artist_detail"),
    path("create-album/", views.AlbumCreateView.as_view(), name="create_album"),
    path("delete-album/<int:album_id>/", views.AlbumDeleteView.as_view(), name="delete_album"),
    path("update-album/<int:album_id>/", views.AlbumUpdateView.as_view(), name="update_album"),
    path("album/<int:album_id>/", views.AlbumDetailView.as_view(), name="album_detail"),
    path("manage/artist/<int:artist_id>/", views.ManageArtistView.as_view(), name="manage_artist"),
    path("create-track/", views.TrackCreateView.as_view(), name="create_track"),
    path("track/<int:track_id>", views.TrackDetailView.as_view(), name="track_detail"),
]
