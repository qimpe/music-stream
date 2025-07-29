import typing

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.http import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponseBase, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, View

from . import services
from .forms import AlbumForm, ArtistCreateForm, TrackInAlbumFormSet
from .mixins import UserHasArtist, UserManageArtist
from .models import Album, Artist, Track


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
    template_name = "music/create_artist.html"

    def form_valid(self, form: ArtistCreateForm) -> HttpResponse:
        artist_service = services.ArtistService()
        self.object = artist_service.create_artist(self.request, form)
        messages.success(self.request, "Карточка успешно создана")
        return redirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse(self.success_url, kwargs={"artist_id": self.object.id})


class ArtistDetailView(DetailView):
    """Детальная страница Артиста."""

    model = Artist
    pk_url_kwarg = "artist_id"
    context_object_name = "artist"
    template_name = "music/artist_detail.html"

    def get_queryset(self) -> QuerySet[Artist]:
        artist_service = services.ArtistService()
        artist_id = self.kwargs.get("artist_id")
        return artist_service.fetch_artist_queryset_by_id(artist_id)

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        artist_album_service = services.AlbumArtistService()
        artist_service = services.ArtistService()
        artist_id = self.kwargs.get("artist_id")
        context = super().get_context_data(**kwargs)
        context["artist_albums"] = artist_album_service.fetch_artist_albums(artist_id)
        context["releases"] = artist_service.fetch_all_artist_releases(artist_id)
        return context


class ManageArtistView(UserManageArtist, View):
    """Страница управления артистом доступная только пользователю,который им обладает."""

    template_name = "music/manage_artist.html"

    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        artist_id = self.kwargs.get("artist_id")
        if artist_id:
            return render(request, self.template_name, context={"artist_id": artist_id})  # type: ignore
        return HttpResponseNotFound()


# *Album views
class AlbumCreateView(LoginRequiredMixin, CreateView):
    """Представление создание альбома и треков которые в него входят."""

    model = Album
    form_class = AlbumForm
    template_name = "music/create_album.html"

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        context = super().get_context_data(**kwargs)
        if "track_formset" in kwargs:
            context["track_formset"] = kwargs["track_formset"]
        else:
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

    def form_valid(self, form: AlbumForm, track_formset) -> HttpResponse:  # type: ignore
        album_service = services.AlbumService()
        self.object = album_service.create_album(self.request.user.id, form, track_formset)  # type: ignore
        return super().form_valid(form)

    def form_invalid(self, album_form: AlbumForm, track_formset) -> HttpResponse:  # type: ignore
        return render(
            self.request,
            self.template_name,  # type: ignore
            {
                "genres": services.GenreService().fetch_all_genres_titles(),
                "album_form": album_form,
                "track_formset": track_formset,
            },
        )

    def get_success_url(self) -> str:
        return reverse("music:album_detail", kwargs={"album_id": self.object.id})


class AlbumDeleteView(LoginRequiredMixin, DeleteView):
    """Представление удаления Album."""

    model = Album
    pk_url_kwarg = "album_id"
    success_url = reverse_lazy("music:index")
    template_name = "music/album_confirm_delete.html"

    def form_valid(self, form: typing.Any) -> HttpResponse:
        album_id = self.kwargs.get("album_id")
        album_service = services.AlbumService()
        album_service.delete_album(album_id)
        return super().form_valid(form)


class AlbumUpdateView(LoginRequiredMixin, UpdateView):
    """Представление обновления данных о альбоме."""

    model = Album
    form_class = AlbumForm
    pk_url_kwarg = "album_id"
    template_name = "music/update_album.html"
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
    template_name = "music/album_detail.html"
    success_url = "music:index"

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


@login_required
def get_track_url(request, track_id):
    Track.objects.get(id=track_id)
    stream_url = f"/stream/{track_id}/"
    return JsonResponse({"url": stream_url})


@login_required
def stream_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    bucket = settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
    key = track.audio_file.name
    print(key)
    internal_path = f"/internal-stream/{bucket}/{key}"
    print(internal_path)
    response = HttpResponse()
    response["X-Accel-Redirect"] = internal_path
    response["Content-Type"] = "audio/mpeg"  # Настройте в зависимости от типа файла
    response["Accept-Ranges"] = "bytes"
    return response
