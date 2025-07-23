import typing

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.views.generic import DetailView

from . import services


# Create your views here.
class ProfileDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Представление профиля пользователя."""

    model = User
    pk_url_kwarg = "user_id"
    context_object_name = "user"
    template_name = "users/user_detail.html"

    def test_func(self) -> bool | None:
        """Проверка является ли пользователь владельцем аккаунта."""
        if self.request.user.id == self.kwargs.get("user_id"):  # type: ignore
            return True
        return None

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        return services.fetch_user_by_id(user.id)  # type: ignore

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["users_artists"] = services.fetch_users_artists_by_user_id(user.id)  # type: ignore
        return context
