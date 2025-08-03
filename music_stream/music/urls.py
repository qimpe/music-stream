"""music_stream URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""

from django.urls import path

from . import views

app_name = "music"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("create-artist/", views.ArtistCreateView.as_view(), name="create_artist"),
    path("artist/<int:artist_id>", views.ArtistDetailView.as_view(), name="artist_detail"),
    path("create-album/", views.AlbumCreateView.as_view(), name="create_album"),
    path("delete-album/<int:album_id>", views.AlbumDeleteView.as_view(), name="delete_album"),
    path("update-album/<int:album_id>", views.AlbumUpdateView.as_view(), name="update_album"),
    path("album/<int:album_id>", views.AlbumDetailView.as_view(), name="album_detail"),
    path("manage/artist/<int:artist_id>", views.ManageArtistView.as_view(), name="manage_artist"),
]
