import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponseBase

from . import services


class UserHasArtist(LoginRequiredMixin):
    """Проверяет обладает ли пользователь артистом."""

    def dispatch(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponseBase:
        service = services.ArtistService()
        if service.is_user_has_artist(request.user.id):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UserManageArtist(LoginRequiredMixin):
    """Проверяет обладает ли пользователь правами на данного артиста."""

    def dispatch(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponseBase:
        service = services.ArtistService()
        artist_id = kwargs.get("artist_id")
        if artist_id:
            artist = service.fetch_artist_by_user_id(request.user.id)  # type: ignore
            if artist_id == artist.id:
                return super().dispatch(request, *args, **kwargs)
        return self.handle_no_permission()
