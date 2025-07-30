import os

import jwt
import requests
from django.contrib.auth import login
from django.core.exceptions import BadRequest
from django.http import HttpResponseBadRequest
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import View
from dotenv import load_dotenv
from users import services

from . import utils

load_dotenv()


class GoogleOAuth(View):
    """Представление генерации ссылки на аутентификацию в сервисе."""

    def get(self, request: HttpRequest) -> HttpResponse:
        service = utils.OAuthService()
        uri = service.generate_google_oauth_redirect_uri()
        return HttpResponseRedirect(uri)


class GoogleOAuthCallback(View):
    """Google OAuth обработчик."""

    success_url = reverse_lazy("music:index")

    def get(self, request: HttpRequest) -> HttpResponse:
        google_token_uri = os.getenv("OAUTH_GOOGLE_TOKEN_URI")
        code = request.GET.get("code")
        if not code:
            raise BadRequest
        if google_token_uri:
            response = requests.post(
                url=google_token_uri,
                timeout=5,
                data={
                    "client_id": os.getenv("OAUTH_GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("OAUTH_GOOGLE_CLIENT_SECRET"),
                    "redirect_uri": "http://localhost:8000/auth/google/callback",
                    "grant_type": "authorization_code",
                    "code": code,
                },
            ).json()
            id_token = response["id_token"]
            # access_token = response["access_token"]
            user_data = jwt.decode(
                id_token,
                algorithms=["RS256"],
                options={"verify_signature": False},
            )
            user_service = services.UserService()
            user = user_service.create_user(user_data["email"])
            if user:
                login(request, user)
                return HttpResponseRedirect(self.success_url)
        return HttpResponseBadRequest("Ошибка")
