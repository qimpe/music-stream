import os
import urllib.parse

from dotenv import load_dotenv

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
