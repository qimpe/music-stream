import requests
from django.contrib import messages
from django.contrib.auth import login
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import View
from dotenv import load_dotenv

from .oauth_config import OAuthFactory, OAuthProvider

load_dotenv()


class OAuthView(View):
    """Представление генерации ссылки на аутентификацию в сервисе."""

    unsuccess_url = reverse_lazy("users:sign_in")

    def get(self, request: HttpRequest, provider: OAuthProvider) -> HttpResponse:
        factory = OAuthFactory.fetch_oauth_provider(provider)
        if not factory:
            return HttpResponseRedirect(self.unsuccess_url)
        uri = factory.create_operations().generate_oauth_redirect_uri()
        return HttpResponseRedirect(uri)


class OAuthCallback(View):
    """Google OAuth обработчик."""

    success_url = reverse_lazy("music:index")
    unsuccess_url = reverse_lazy("users:sign_in")

    def get(self, request: HttpRequest, provider: OAuthProvider) -> HttpResponse:
        factory = OAuthFactory.fetch_oauth_provider(provider)
        if not factory:
            return HttpResponseBadRequest("Ошибка")
        operations = factory.create_operations()
        code = request.GET.get("code")
        if not code:
            return HttpResponseBadRequest("Нет кода, попробуйте обычную регистрацию")
        token_uri = operations.config["TOKEN_URI"]
        if token_uri:
            payload = operations.get_payload_for_access_token_request(code)
            headers = operations.get_headers_for_access_token_request()
            response = requests.post(url=token_uri, timeout=5, data=payload, headers=headers)
            user = operations.process_data_after_code_exchange(response)
            if user:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {user.username}!")
                return HttpResponseRedirect(self.success_url)
        messages.error(request, f"Произошла ошибка при использовании {provider}")
        return HttpResponseRedirect(self.unsuccess_url)
