import os
import urllib.parse
from abc import ABC, abstractmethod
from typing import Literal, Optional, TypedDict, TypeVar

import jwt
import requests
from apps.users.services import UserService
from config.settings import constants
from django.contrib.auth.models import User
from dotenv import load_dotenv
from requests.adapters import Response

load_dotenv()


OAuthProvider = Literal["github", "google"]


class GoogleProviderParamsConfig(TypedDict):
    """Конфигурация параметров запроса для Провайдера GOOGLE."""

    client_id: str
    redirect_uri: str
    response_type: str
    scope: str
    access_type: str
    prompt: str


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
            "BASE_REDIRECT_URI": constants.GITHUB_OAUTH_REDIRECT_URI,
            "BASE_URL": constants.GITHUB_OAUTH_BASE_URL,
        },
        "google": {
            "CLIENT_SECRET": os.getenv("OAUTH_GOOGLE_CLIENT_SECRET", ""),
            "CLIENT_ID": os.getenv("OAUTH_GOOGLE_CLIENT_ID", ""),
            "TOKEN_URI": "https://oauth2.googleapis.com/token",
            "BASE_REDIRECT_URI": constants.GOOGLE_OAUTH_REDIRECT_URI,
            "BASE_URL": constants.GOOGLE_OAUTH_BASE_URL,
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

    @abstractmethod
    def get_headers_for_access_token_request(self) -> dict:
        """Добавляет заголовки для запроса на access_token."""


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
        self.__config = OAuthConfig.auth_services["google"]

    @property
    def config(self) -> ProviderConfig:
        return self.__config

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
            "prompt": "select_account",
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
        id_token = response.json().get("id_token")
        user_data = jwt.decode(
            id_token,
            algorithms=["RS256"],
            options={"verify_signature": False},
        )
        user_service = UserService()
        if (email := user_data.get("email")) and (user := user_service.get_or_create_user(email)):
            return user
        return None

    def get_headers_for_access_token_request(self) -> dict:
        return {"Content-Type": "application/x-www-form-urlencoded"}


# TODO make a state
class GithubOAuthOperations(OAuthOperations):
    def __init__(self) -> None:
        self.__config = OAuthConfig.auth_services["github"]

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
            "scope": "user",
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
        access_token = response.json().get("access_token")
        user_data = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5,
        ).json()
        user_service = UserService()
        if email := not user_data.get("email"):
            return None
        kwargs = {"email": email, "username": user_data.get("login")}
        if user := user_service.get_or_create_user(**kwargs):
            return user
        return None

    def get_headers_for_access_token_request(self) -> dict:
        """Добавляет заголовки для запроса на access_token."""
        return {"Accept": "application/json"}


class GoogleOAuthFactory(OAuthFactory):
    def create_operations(self) -> GoogleOAuthOperations:
        return GoogleOAuthOperations()


class GithubOAuthFactory(OAuthFactory):
    def create_operations(self) -> GithubOAuthOperations:
        return GithubOAuthOperations()
