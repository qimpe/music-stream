import requests
from django.contrib.auth import login
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import View
from dotenv import load_dotenv

from .oauth_config import OAuthConfig

load_dotenv()


class OAuthView(View):
    """Представление генерации ссылки на аутентификацию в сервисе."""

    def get(self, request: HttpRequest, provider: str) -> HttpResponse:
        uri = OAuthConfig.generate_oauth_redirect_uri(provider)
        print(uri)
        return HttpResponseRedirect(uri)


class OAuthCallback(View):
    """Google OAuth обработчик."""

    success_url = reverse_lazy("music:index")

    def get(self, request: HttpRequest, provider: str) -> HttpResponse:
        provider_config = OAuthConfig.fetch_provider_config(provider)
        code = request.GET.get("code")
        if not code:
            return HttpResponseBadRequest("Нет кода, попробуйте обычную регистрацию")
        token_uri = provider_config["TOKEN_URI"]
        if token_uri:
            payload = OAuthConfig.get_payload_for_access_token_request(provider, code)
            response = requests.post(url=token_uri, timeout=5, data=payload)
            response.json()["id_token"]
            print(f"{provider} - {response}")
            user = OAuthConfig.process_data_after_code_exchange(provider, response)
            if user:
                login(request, user)
                return HttpResponseRedirect(self.success_url)
            return None
        return None


"""id_token = response["id_token"]
                user_data = jwt.decode(
                    id_token,
                    algorithms=["RS256"],
                    options={"verify_signature": False},
                )
                user_service = UserService()
                user = user_service.create_user(user_data["email"])
                if user:
                    login(request, user)
                    return HttpResponseRedirect(self.success_url)
            else:
                response = requests.post(
                    url=google_token_uri,
                    timeout=5,
                    data={
                        "client_id": provider_config["CLIENT_ID"],
                        "client_secret": provider_config["CLIENT_SECRET"],
                        "redirect_uri": provider_config["BASE_REDIRECT_URI"],
                        "code": code,
                    },
                )

            return HttpResponseBadRequest("Какая-то хуйня c пользователем")
        return HttpResponseBadRequest("Какая-то хуйня")
"""
