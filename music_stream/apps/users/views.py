import typing

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, DetailView

from . import services
from .forms import SignInForm, SignUpForm


class SignUpView(CreateView):
    """Представление регистрации аккаунта."""

    form_class = SignUpForm
    template_name = "apps/users/sign_up.html"


class SignInView(LoginView):
    """Представление входа из аккаунта."""

    form_class = SignInForm
    template_name = "apps/users/sign_in.html"
    redirect_authenticated_user = True


class SignOutView(LogoutView):
    """Представление выхода из аккаунта."""


class ProfileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Представление профиля пользователя."""

    model = User
    pk_url_kwarg = "user_id"
    context_object_name = "user"
    template_name = "apps/users/user_detail.html"

    def test_func(self) -> bool | None:
        """Проверка является ли пользователь владельцем аккаунта."""
        if self.request.user.pk == self.kwargs.get("user_id"):
            return True
        return None

    def get_object(self, queryset: services.QuerySet | None = ...) -> typing.Any:
        self.object = self.request.user
        return self.object

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)
        user = self.object
        service = services.ArtistService()
        context["user_artist"] = service.fetch_artist_by_user_id(user.pk)
        return context
