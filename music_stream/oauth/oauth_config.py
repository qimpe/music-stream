import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Literal, Optional, TypedDict, TypeVar

import jwt
from django.contrib.auth.models import User
from dotenv import load_dotenv
from requests.adapters import Response
from users.services import UserService

load_dotenv()


OAuthProvider = Literal["github", "google"]


class GoogleProviderParamsConfig(TypedDict):
    """Конфигурация параметров запроса для Провайдера GOOGLE."""

    client_id: str
    redirect_uri: str
    response_type: str
    scope: str
    access_type: str


class GithubProviderParamsConfig(TypedDict):
    """Конфигурация параметров запроса для Провайдера GITHUB."""

    client_id: str
    redirect_uri: str
    scope: str


class ProviderConfig(TypedDict):
    """Конфигурация для Провайдера."""

    CLIENT_SECRET: str
    CLIENT_ID: str
    TOKEN_URI: str
    BASE_REDIRECT_URI: str
    BASE_URL: str


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


T = TypeVar("T", bound="OAuthOperations")


class OAuthOperations(ABC):
    """Общий класс операций для OAuth провайдеров."""

    @property
    @abstractmethod
    def config(self) -> ProviderConfig:
        """Абстрактное свойство для конфигурации провайдера."""

    @abstractmethod
    def generate_oauth_redirect_uri(self) -> str:
        """Возвращает ссылку для аутентификации."""

    @abstractmethod
    def generate_provider_params(self) -> GoogleProviderParamsConfig | GithubProviderParamsConfig:
        """Возвращает конфиг запроса провайдера по запросу."""

    @abstractmethod
    def fetch_redirect_url(self) -> str:
        """Возвращает url для конкретного провайдера."""

    @abstractmethod
    def get_payload_for_access_token_request(self, code: str) -> dict:
        """Возвращает payload для запроса на обмен кода авторизации."""

    @abstractmethod
    def process_data_after_code_exchange(self, response: Response) -> User | None:
        """Обработка данных, которые пришли после обмена кода на access токен."""


class OAuthFactory(ABC):
    """Абстрактная фабрика провайдеров OAuth."""

    @abstractmethod
    def create_operations(self) -> OAuthOperations:
        pass

    @staticmethod
    def fetch_oauth_provider(provider_name: OAuthProvider) -> Optional["OAuthFactory"]:
        """Возвращает фабрику провайдера по названию."""
        factories: dict[OAuthProvider, type[OAuthFactory]] = {
            "google": GoogleOAuthFactory,
            "github": GithubOAuthFactory,
        }
        if factory_class := factories.get(provider_name):
            return factory_class()
        return None


class GoogleOAuthOperations(OAuthOperations):
    def __init__(self) -> None:
        self._config = OAuthConfig.auth_services["google"]

    @property
    def config(self) -> ProviderConfig:
        return self._config

    def generate_oauth_redirect_uri(self) -> str:
        base_url = self.config["BASE_URL"]
        params = self.generate_provider_params()
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"{base_url}?{query_string}"

    def generate_provider_params(self) -> GoogleProviderParamsConfig:
        return {
            "client_id": self.config["CLIENT_ID"],
            "redirect_uri": self.config["BASE_REDIRECT_URI"],
            "response_type": "code",
            "scope": "openid profile email",
            "access_type": "offline",
        }

    def fetch_redirect_url(self) -> str:
        return self.config["BASE_REDIRECT_URI"]

    def get_payload_for_access_token_request(self, code: str) -> dict:
        return {
            "client_id": self.config["CLIENT_ID"],
            "client_secret": self.config["CLIENT_SECRET"],
            "redirect_uri": self.config["BASE_REDIRECT_URI"],
            "grant_type": "authorization_code",
            "code": code,
        }

    def process_data_after_code_exchange(self, response: Response) -> User | None:
        print(response.json())
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


class GithubOAuthOperations(OAuthOperations):
    __config = OAuthConfig.auth_services["github"]

    @property
    def config(self) -> ProviderConfig:
        return self.__config

    def generate_oauth_redirect_uri(self) -> str:
        base_url = self.config["BASE_URL"]
        params = self.generate_provider_params()
        query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
        return f"{base_url}?{query_string}"

    def generate_provider_params(self) -> GithubProviderParamsConfig:
        return {
            "client_id": self.config["CLIENT_ID"],
            "redirect_uri": self.config["BASE_REDIRECT_URI"],
            "scope": "user:email",
        }

    def fetch_redirect_url(self) -> str:
        return self.config["BASE_REDIRECT_URI"]

    def get_payload_for_access_token_request(self, code: str) -> dict:
        return {
            "client_id": self.config["CLIENT_ID"],
            "client_secret": self.config["CLIENT_SECRET"],
            "redirect_uri": self.config["BASE_REDIRECT_URI"],
            "grant_type": "authorization_code",
            "code": code,
        }

    def process_data_after_code_exchange(self, response: Response) -> User | None:
        print(response.json())
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


class GoogleOAuthFactory(OAuthFactory):
    def create_operations(self) -> GoogleOAuthOperations:
        return GoogleOAuthOperations()


class GithubOAuthFactory(OAuthFactory):
    def create_operations(self) -> GoogleOAuthOperations:
        return GoogleOAuthOperations()
