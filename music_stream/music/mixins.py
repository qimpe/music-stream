import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponseBase

from . import services


class UserManageArtist(LoginRequiredMixin):
    def dispatch(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponseBase:
        service = services.UserArtistService()
        artist = service.fetch_artist_by_user_id(request.user.id)  # type: ignore
        print(request.user)
        print(artist.user)
        if request.user != artist.user or artist.user is None:  # type: ignore
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
