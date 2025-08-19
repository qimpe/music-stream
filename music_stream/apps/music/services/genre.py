
from apps.music.models import Genre


class GenreService:
    """Сервис для модели: Genre."""

    def fetch_all_genres_titles(self) -> list[str]:
        """Возвращает список названий всех жанров, упорядоченных по названию."""
        return list(Genre.objects.order_by("title").values_list("title", flat=True))

    def fetch_genre_by_title(self, title: str) -> Genre | None:
        """Возвращает объект жанра оп его названию."""
        try:
            return Genre.objects.get(title=title)
        except Genre.DoesNotExist:
            return None
