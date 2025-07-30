import os
from typing import Literal, TypedDict

from dotenv import load_dotenv

load_dotenv()


class ProviderConfig(TypedDict):
    """Конфигурация для Провайдера."""

    CLIENT_SECRET: str
    CLIENT_ID: str
    TOKEN_URI: str


OAuthProvider = Literal["github", "google"]


class OAuthConfig:
    """Централизованная конфигурация OAuth-провайдеров."""

    auth_services: dict[OAuthProvider, ProviderConfig] = {
        "github": {
            "CLIENT_SECRET": os.getenv("OAUTH_GITHUB_CLIENT_SECRET", ""),
            "CLIENT_ID": os.getenv("CLIENT_ID", ""),
            "TOKEN_URI": "https://oauth2.googleapis.com/token",
        },
        "google": {
            "CLIENT_SECRET": os.getenv("OAUTH_GOOGLE_CLIENT_SECRET", ""),
            "CLIENT_ID": os.getenv("OAUTH_GOOGLE_CLIENT_ID", ""),
            "TOKEN_URI": "https://github.com/login/oauth/authorize",
        },
    }

    @classmethod
    def fetch_provider_config(cls, provider: OAuthProvider) -> OAuthConfig:
        """Возвращает конфиг провайдера OAuth."""
        cls.auth_services.get(provider)
