import os
import urllib.parse
from typing import Literal, TypedDict

import jwt
from django.contrib.auth.models import User
from dotenv import load_dotenv
from requests.adapters import Response
from users.services import UserService

load_dotenv()


OAuthProvider = Literal["github", "google"]


class ProviderConfig(TypedDict):
    """Конфигурация для Провайдера."""

    CLIENT_SECRET: str
    CLIENT_ID: str
    TOKEN_URI: str
    BASE_REDIRECT_URI: str
    BASE_URL: str


class GoogleProviderParamsConfig(TypedDict):
    """Конфигурация параметров для Провайдера GOOGLE."""

    client_id: str
    redirect_uri: str
    response_type: str
    scope: str
    access_type: str


class GithubProviderParamsConfig(TypedDict):
    """Конфигурация параметров для Провайдера GITHUB."""

    client_id: str
    redirect_uri: str
    scope: str


providers_configs = {"github": GithubProviderParamsConfig, "google": GoogleProviderParamsConfig}


class OAuthConfig:
    """Централизованная конфигурация OAuth-провайдеров."""

    auth_services: dict[OAuthProvider, ProviderConfig] = {
        "github": {
            "CLIENT_SECRET": os.getenv("OAUTH_GITHUB_CLIENT_SECRET", ""),
            "CLIENT_ID": os.getenv("OAUTH_GITHUB_CLIENT_ID", ""),
            "TOKEN_URI": "https://github.com/login/oauth/access_token",
            "BASE_REDIRECT_URI": "http://localhost:8000/oauth2/github/callback",
            "BASE_URL": "https://github.com/login/oauth/authorize",
        },
        "google": {
            "CLIENT_SECRET": os.getenv("OAUTH_GOOGLE_CLIENT_SECRET", ""),
            "CLIENT_ID": os.getenv("OAUTH_GOOGLE_CLIENT_ID", ""),
            "TOKEN_URI": "https://oauth2.googleapis.com/token",
            "BASE_REDIRECT_URI": "http://localhost:8000/oauth2/google/callback",
            "BASE_URL": "https://accounts.google.com/o/oauth2/v2/auth",
        },
    }

    @classmethod
    def generate_provider_params(
        cls, provider: OAuthProvider
    ) -> GoogleProviderParamsConfig | GithubProviderParamsConfig:
        """Возвращает конфиг запроса провайдера по запросу."""
        provider_config = cls.auth_services[provider]
        if provider == "google":
            google_params: GoogleProviderParamsConfig = {
                "client_id": provider_config["CLIENT_ID"],
                "redirect_uri": provider_config["BASE_REDIRECT_URI"],
                "response_type": "code",
                "scope": "openid profile email",
                "access_type": "offline",
            }
            return google_params
        if provider == "github":
            github_params: GithubProviderParamsConfig = {
                "client_id": provider_config["CLIENT_ID"],
                "redirect_uri": provider_config["BASE_REDIRECT_URI"],
                "scope": "user:email",
            }
            return github_params
        raise ValueError

    @classmethod
    def generate_oauth_redirect_uri(cls, provider: OAuthProvider) -> str:
        """Возвращает ссылку для аутентификации."""
        config = OAuthConfig.fetch_provider_config(provider)
        base_url = config["BASE_URL"]
        params = OAuthConfig.generate_provider_params(provider)
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"{base_url}?{query_string}"

    @classmethod
    def fetch_redirect_url(cls, provider: OAuthProvider) -> str:
        """Возвращает url для конкретного провайдера."""
        return cls.auth_services[provider]["BASE_REDIRECT_URI"]

    @classmethod
    def fetch_provider_config(cls, provider: OAuthProvider) -> ProviderConfig:
        """Возвращает конфиг провайдера OAuth."""
        if provider_config := cls.auth_services.get(provider):
            return provider_config
        msg = f"{provider} does not exist"
        raise ValueError(msg)

    @classmethod
    def get_payload_for_access_token_request(cls, provider: OAuthProvider, code: str) -> dict:
        """Возвращает payload для запроса на обмен кода авторизации."""
        provider_config = OAuthConfig.fetch_provider_config(provider)
        provider_config["TOKEN_URI"]
        if provider == "google":
            return {
                "client_id": provider_config["CLIENT_ID"],
                "client_secret": provider_config["CLIENT_SECRET"],
                "redirect_uri": provider_config["BASE_REDIRECT_URI"],
                "grant_type": "authorization_code",
                "code": code,
            }
        if provider == "github":
            return {
                "client_id": provider_config["CLIENT_ID"],
                "client_secret": provider_config["CLIENT_SECRET"],
                "redirect_uri": provider_config["BASE_REDIRECT_URI"],
                "code": code,
            }
        return None

    @classmethod
    def process_data_after_code_exchange(cls, provider: OAuthProvider, response: Response) -> User | None:
        """Обработка данных, которые пришли после обмена кода на access токен."""
        if provider == "google":
            response = response.json()
            id_token = response["id_token"]  # type: ignore
            user_data = jwt.decode(
                id_token,
                algorithms=["RS256"],
                options={"verify_signature": False},
            )
            user_service = UserService()
            if user := user_service.get_or_create_user(user_data["email"]):
                return user
        return None
