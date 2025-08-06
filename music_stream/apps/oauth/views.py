import logging

import requests
from django.contrib import messages
from django.contrib.auth import login
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import View
from dotenv import load_dotenv

from .oauth_config import OAuthFactory, OAuthProvider

load_dotenv()

logger = logging.getLogger(__name__)


class OAuthView(View):
    """Представление генерации ссылки на аутентификацию в сервисе."""

    unsuccess_url = reverse_lazy("users:sign_in")

    def get(self, request: HttpRequest, provider: OAuthProvider) -> HttpResponse:
        factory = OAuthFactory.fetch_oauth_provider(provider)
        if not factory:
            logger.error(f"Error of fetching {provider} in OAuthFactory")
            msg = f"Ошибка {provider}, попробуйте другой способ."
            messages.error(request, msg)
            return HttpResponseRedirect(self.unsuccess_url)

        uri = factory.create_operations().generate_oauth_redirect_uri()
        return HttpResponseRedirect(uri)


class OAuthCallback(View):
    """Google OAuth обработчик."""

    success_url = reverse_lazy("music:index")
    error_url = reverse_lazy("users:sign_in")

    def get(self, request: HttpRequest, provider: OAuthProvider) -> HttpResponse:  # noqa: PLR0911
        factory = OAuthFactory.fetch_oauth_provider(provider)
        if not factory:
            logger.error(f"Error of fetching {provider} in OAuthFactory")
            msg = f"Ошибка {provider}, попробуйте другой способ."
            messages.error(request, msg)
            return HttpResponseRedirect(self.error_url)

        code = request.GET.get("code")
        if not code:
            logger.error(f"No code from {provider}")
            msg = f"Ошибка авторизации в {provider}, попробуйте другой способ."
            messages.error(request, msg)
            return HttpResponseRedirect(self.error_url)

        operations = factory.create_operations()
        token_uri = operations.config["TOKEN_URI"]
        if not token_uri:
            logger.error("TOKEN_URI is None")
            msg = f"Ошибка авторизации в {provider}, попробуйте другой способ."
            messages.error(request, msg)
            return HttpResponseRedirect(self.error_url)

        try:
            payload = operations.get_payload_for_access_token_request(code)
            headers = operations.get_headers_for_access_token_request()
            response = requests.post(url=token_uri, timeout=10, data=payload, headers=headers)
            response.raise_for_status()
            user = operations.process_data_after_code_exchange(response)
            if not user:
                logger.error("Error of creation user")
                msg = f"Ошибка авторизации через {provider}"
                messages.error(request, msg)
                return HttpResponseRedirect(self.error_url)

            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return HttpResponseRedirect(self.success_url)

        except requests.RequestException:
            logger.exception("Exception in OAuthCallback in request")
            msg = f"Ошибка авторизации через {provider}"
            messages.error(request, msg)
            return HttpResponseRedirect(self.error_url)

        except Exception:
            logger.exception("Exception in OAuthCallback")
            msg = f"Ошибка авторизации через {provider}"
            messages.error(request, msg)
        return HttpResponseRedirect(self.error_url)
