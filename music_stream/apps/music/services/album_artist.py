from django.db.models import QuerySet

from apps.music.models import Album, AlbumArtist, Artist


class AlbumArtistService:
    """Сервис для модели: AlbumArtist."""

    def create_artist_album(self, artist: Artist, album: Album) -> None:
        """Привязывает альбом к артисту."""
        AlbumArtist.objects.create(artist=artist, album=album)

    def fetch_artist_albums(self, artist_id: int) -> QuerySet[AlbumArtist]:
        """Возвращает все альбомы артиста по его id и загружает объекты альбомов."""
        return AlbumArtist.objects.filter(artist_id=artist_id)
