import os
import urllib.parse

from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from dotenv import load_dotenv
from music.models import Artist
from music.services import ArtistService

load_dotenv()


class OAuthService:
    """Сервис для авторизации через OAuth 2.0."""

    def generate_google_oauth_redirect_uri(self) -> str:
        """Возвращает ссылку для аутентификации."""
        base_url = os.getenv("GOOGLE_OAUTH_BASE_URL")
        params = {
            "client_id": os.getenv("OAUTH_GOOGLE_CLIENT_ID"),
            "redirect_uri": os.getenv("GOOGLE_OAUTH_REDIRECT_URI"),
            "response_type": "code",
            "scope": "email openid profile",
            "access_type": "offline",
        }
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"{base_url}?{query_string}"


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
