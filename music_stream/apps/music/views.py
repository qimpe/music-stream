import logging
import typing

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponseBase, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View

from . import services
from .forms import AlbumForm, ArtistCreateForm, TrackCreateForm, TrackInAlbumFormSet
from .mixins import UserHasArtist, UserManageArtist
from .models import Album, Artist, Track

logger = logging.getLogger(__name__)


# * index
class IndexView(View):
    """Главная страница."""

    template_name = "index.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)


# *Artist views
class ArtistCreateView(UserHasArtist, CreateView):
    """Представление создания карточки артиста."""

    model = Artist
    form_class = ArtistCreateForm
    success_url = "music:artist_detail"
    template_name = "apps/music/create_artist.html"

    def form_valid(self, form: ArtistCreateForm) -> HttpResponse:
        artist_service = services.ArtistService()
        self.object = artist_service.create_artist(self.request.user, form)  # pyright: ignore[reportArgumentType]
        messages.success(self.request, "Карточка успешно создана")
        return redirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse(self.success_url, kwargs={"artist_id": self.object.id})  # pyright: ignore[reportOptionalMemberAccess]


class ArtistDetailView(DetailView):
    """Детальная страница Артиста."""

    model = Artist
    pk_url_kwarg = "artist_id"
    context_object_name = "artist"
    template_name = "apps/music/artist_detail.html"

    def get_queryset(self) -> QuerySet[Artist]:
        artist_service = services.ArtistService()
        return artist_service.fetch_artist_queryset_by_id(self.kwargs.get("artist_id"))

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        artist_album_service = services.AlbumArtistService()
        artist_service = services.ArtistService()
        context = super().get_context_data(**kwargs)
        if artist_id := self.kwargs.get("artist_id"):
            context["artist_albums"] = artist_album_service.fetch_artist_albums(artist_id)
            context["releases"] = artist_service.fetch_all_artist_releases(artist_id)
        return context


class ManageArtistView(UserManageArtist, View):
    """Страница управления артистом доступная только пользователю,который им обладает."""

    template_name = "apps/music/manage_artist.html"

    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        if self.artist:
            return render(request, self.template_name, context={"artist_id": self.artist.id, "artist": self.artist})  # type: ignore
        return HttpResponseNotFound()


# *Album views
class AlbumCreateView(LoginRequiredMixin, CreateView):
    """Представление создание альбома и треков которые в него входят."""

    model = Album
    form_class = AlbumForm
    template_name = "apps/music/create_album.html"

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)
        context["track_formset"] = TrackInAlbumFormSet(prefix="tracks")
        context["genres"] = services.GenreService().fetch_all_genres_titles()
        return context

    def post(self, request: HttpRequest, *args: reverse_lazy, **kwargs: reverse_lazy) -> HttpResponse:  # type: ignore
        self.object = None
        album_form = self.get_form()
        track_formset = TrackInAlbumFormSet(request.POST, request.FILES, prefix="tracks")
        if album_form.is_valid() and track_formset.is_valid():
            return self.form_valid(album_form, track_formset)
        return self.form_invalid(album_form, track_formset)

    def form_valid(self, form: AlbumForm, track_formset: inlineformset_factory) -> HttpResponse:  # type: ignore
        album_service = services.AlbumService()
        self.object = album_service.create_album(self.request.user.id, form, track_formset)  # type: ignore
        messages.success(self.request, "Альбом создан и отправлен на модерацию")
        return super().form_valid(form)

    def form_invalid(self, album_form: AlbumForm, track_formset: inlineformset_factory) -> HttpResponse:  # type: ignore
        logger.debug(album_form.data)
        return self.render_to_response(self.get_context_data(album_form=album_form, track_formset=track_formset))

    def get_success_url(self) -> str:
        return reverse("users:profile", kwargs={"user_id": self.request.user.id})


class AlbumDeleteView(UserManageArtist, DeleteView):
    """Представление удаления Album."""

    model = Album
    pk_url_kwarg = "album_id"
    success_url = reverse_lazy("music:index")
    template_name = "apps/music/album_confirm_delete.html"

    def form_valid(self, form: typing.Any) -> HttpResponse:
        album_id = self.kwargs.get("album_id")
        album_service = services.AlbumService()
        album_service.delete_album(album_id)
        return super().form_valid(form)


class AlbumUpdateView(UserManageArtist, UpdateView):
    """Представление обновления данных о альбоме."""

    model = Album
    form_class = AlbumForm
    pk_url_kwarg = "album_id"
    template_name = "apps/music/update_album.html"
    success_url = "music:index"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect | HttpResponseBase:
        try:
            return super().dispatch(request, *args, **kwargs)
        except (Album.DoesNotExist, PermissionDenied) as e:
            msg = "Альбом не найден" if isinstance(e, Album.DoesNotExist) else str(e)
            messages.error(request, msg)
            return redirect(self.get_success_url())

    def get_object(self, queryset: QuerySet | None = ...) -> Album:  # pyright: ignore[reportArgumentType]
        album_id = self.kwargs.get(self.pk_url_kwarg)
        album_service = services.AlbumService()
        return album_service.fetch_album_for_update(album_id)


class AlbumDetailView(DetailView):
    model = Album
    pk_url_kwarg = "album_id"
    success_url = "music:index"
    template_name = "apps/music/album_detail.html"

    def get_object(self, queryset: QuerySet | None = ...) -> typing.Any:  # pyright: ignore[reportArgumentType]
        album_service = services.AlbumService()
        return album_service.fetch_album_by_id(self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        album_tracks_service = services.TrackInAlbumService()
        context = super().get_context_data(**kwargs)
        tracks = album_tracks_service.fetch_tracks_in_album(self.object.id)
        context["album_length"] = album_tracks_service.count_album_length_in_minutes(tracks)
        context["album_tracks"] = tracks
        return context


class TrackCreateView(LoginRequiredMixin, CreateView):
    """Представление создания трека."""

    model = Track
    form_class = TrackCreateForm
    success_url = "music:index"
    template_name = "apps/music/create_track.html"

    def form_valid(self, form: TrackCreateForm) -> HttpResponse:
        if user_id := self.request.user.id:
            track_service = services.TrackService()
            track_service.create_track(user_id, form)  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]
            messages.success(self.request, "Трек создан и уже обрабатывается")
            return redirect(reverse_lazy(self.success_url))
        return self.form_invalid(form)


class TrackDetailView(LoginRequiredMixin, DetailView):
    """Представление просмотра страницы трека."""

    model = Track
    pk_url_kwarg = "track_id"
    template_name = "apps/music/track_detail.html"
