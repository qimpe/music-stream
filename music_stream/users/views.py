import os
import typing

import jwt
import requests
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseBadRequest
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, View
from dotenv import load_dotenv

from . import services
from .forms import SignInForm, SignUpForm

load_dotenv()


class GoogleOAuth(View):
    """Представление генерации ссылки на аутентификацию в сервисе."""

    def get(self, request: HttpRequest) -> HttpResponse:
        service = services.OAuthService()
        uri = service.generate_google_oauth_redirect_uri()
        return HttpResponseRedirect(uri)


class GoogleOAuthCallback(View):
    """Google OAuth обработчик."""

    success_url = reverse_lazy("music:index")

    def get(self, request: HttpRequest) -> HttpResponse:
        google_token_uri = os.getenv("OAUTH_GOOGLE_TOKEN_URI")
        code = request.GET.get("code")
        if not code:
            return None
        if google_token_uri:
            response = requests.post(
                url=google_token_uri,
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


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "users/sign_up.html"


class SignInView(LoginView):
    form_class = SignInForm
    template_name = "users/sign_in.html"
    redirect_authenticated_user = True


class SignOutView(LogoutView):
    pass


class ProfileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Представление профиля пользователя."""

    model = User
    pk_url_kwarg = "user_id"
    context_object_name = "user"
    template_name = "users/user_detail.html"

    def test_func(self) -> bool | None:
        """Проверка является ли пользователь владельцем аккаунта."""
        if self.request.user.pk == self.kwargs.get("user_id"):
            return True
        return None

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        user = self.request.user
        context = super().get_context_data(**kwargs)
        service = services.ArtistService()
        context["user_artist"] = service.fetch_artist_by_user_id(user.id)
        return context
