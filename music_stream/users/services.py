from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from music.models import Artist
from music.services import ArtistService


class UserService:
    """Сервис для модели: User."""

    def create_user(self, email: str) -> User:
        """Создает пользователя и возвращает его."""
        return User.objects.create_user(email=email, username=email)

    def fetch_user_by_id(self, user_id: int) -> QuerySet[User]:
        """Возвращает пользователя по его id."""
        return User.objects.filter(id=user_id)

    def fetch_user_artist_by_user_id(self, user_id: int) -> Artist | None:
        """Возвращает всех артистов которыми управляет пользователь."""
        service = ArtistService()
        return service.fetch_artist_by_user_id(user_id)
