from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from music.models import UserArtist


def fetch_user_by_id(user_id: int) -> QuerySet[User]:
    """Возвращает пользователя по его id."""
    return User.objects.filter(id=user_id)


def fetch_users_artists_by_user_id(user_id: int) -> QuerySet[UserArtist]:
    """Возвращает всех артистов которыми управляет пользователь."""
    return UserArtist.objects.select_related("artist").filter(user_id=user_id)
