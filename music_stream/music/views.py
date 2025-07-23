import typing

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, View

from . import services
from .forms import AlbumCreateForm, ArtistCreateForm, TrackInAlbumFormSet
from .models import Album, Artist


# * index
class IndexView(View):
    """Главная страница."""

    template_name = "index.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)


# *Artist views


class ArtistCreateView(LoginRequiredMixin, CreateView):
    """Представление создания Артиста."""

    model = Artist
    success_url = reverse_lazy("music:index")
    form_class = ArtistCreateForm
    template_name = "music/create_artist.html"

    def form_valid(self, form: ArtistCreateForm) -> HttpResponse:
        artist_service = services.ArtistService()
        try:
            artist_service.create_artist(self.request, form)
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Ошибка при создании артиста: {e}")
            return self.form_invalid(form)


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
        artist_id = self.kwargs.get("artist_id")
        context = super().get_context_data(**kwargs)
        context["artist_albums"] = artist_album_service.fetch_artist_albums(artist_id)
        # context["tracks"]=
        return context


# *album views
class AlbumCreateView(LoginRequiredMixin, CreateView):
    """Представление создание альбома и треков которые в него входят."""

    model = Album
    form_class = AlbumCreateForm
    success_url = reverse_lazy("music:index")
    template_name = "music/create_album.html"

    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        return render(
            request,
            self.template_name,  # type: ignore
            {"album_form": AlbumCreateForm(), "track_formset": TrackInAlbumFormSet(prefix="tracks")},
        )

    def post(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        album_form = AlbumCreateForm(request.POST, request.FILES)
        track_formset = TrackInAlbumFormSet(request.POST, request.FILES, prefix="tracks")

        if album_form.is_valid() and track_formset.is_valid():
            album_service = services.AlbumService()
            album_service.create_album(request.user.id, album_form, track_formset)  # type: ignore
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {"album_form": album_form, "track_formset": track_formset},
        )
