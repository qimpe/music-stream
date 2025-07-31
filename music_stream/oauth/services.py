import urllib.parse

from dotenv import load_dotenv
from oauth_config import OAuthConfig, OAuthProvider

load_dotenv()


class OAuthService:
    """Сервис для авторизации через OAuth 2.0."""

    def __init__(self, provider_name: OAuthProvider) -> None:
        self.provider_name: OAuthProvider = provider_name

    def generate_google_oauth_redirect_uri(self) -> str:
        """Возвращает ссылку для аутентификации."""
        config = OAuthConfig.fetch_provider_config(self.provider_name)
        base_url = config["TOKEN_URI"]
        params = {
            "client_id": config["CLIENT_ID"],
            "redirect_uri": config["CLIENT_SECRET"],
            "response_type": "code",
            "scope": "email openid profile",
            "access_type": "offline",
        }
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"{base_url}?{query_string}"


"""class OAuthService:


    def __init__(self, provider_name: OAuthProvider) -> None:
        self.provider_name = provider_name

    def generate_google_oauth_redirect_uri(self) -> str:

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
"""
