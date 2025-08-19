from apps.music.models import AlbumGenres


class GenreAlbumService:
    """Сервис для модели: GenreAlbum."""

    def set_genre_for_album(self, album_id: int, genre_id: int) -> AlbumGenres:
        """Связывает альбом и жанр в отдельную модель."""
        return AlbumGenres.objects.create(album_id=album_id, genre_id=genre_id)
