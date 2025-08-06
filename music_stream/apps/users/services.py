from django.contrib.auth.models import User
from django.db.models.query import QuerySet

from apps.music.models import Artist
from apps.music.services import ArtistService


class UserService:
    """Сервис для модели: User."""

    def get_or_create_user(self, email: str, username: str | None = None) -> User:
        """Проверяет есть ли уже зарегистрированный пользователь, если нет то создает, если есть то возвращает."""
        if not username:
            username = email
        user, created = User.objects.get_or_create(email=email, username=username)
        return user

    def fetch_user_by_id(self, user_id: int) -> QuerySet[User]:
        """Возвращает пользователя по его id."""
        return User.objects.filter(id=user_id)

    def fetch_user_artist_by_user_id(self, user_id: int) -> Artist | None:
        """Возвращает всех артистов которыми управляет пользователь."""
        service = ArtistService()
        return service.fetch_artist_by_user_id(user_id)
