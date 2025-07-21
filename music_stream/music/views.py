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


class IndexView(View):
    """Главная страница."""

    template_name = "index.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)


# *Artist views


class ArtistCreateView(LoginRequiredMixin, CreateView):
    """Представление создания Артиста."""

    model = Artist
    form_class = ArtistCreateForm
    template_name = "music/create_artist.html"
    success_url = "music:index"

    def form_valid(self, form: ArtistCreateForm) -> HttpResponse:
        artist = services.create_artist(self.request, form)
        if artist:
            return redirect(self.get_success_url())
        messages.error(self.request, "Произошла ошибка при созданиии артиста")
        return self.form_invalid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(self.success_url)


class ArtistDetailView(DetailView):
    """Детальная страница Артиста."""

    model = Artist
    slug_url_kwarg = "slug"
    template_name = "music/artist_detail.html"
    context_object_name = "artist"

    def get_queryset(self) -> QuerySet[Artist]:
        slug: str = self.kwargs["slug"]
        return services.fetch_artist_queryset_by_slug(slug)

    def get_context_data(self, **kwargs: typing.Any) -> dict[str, typing.Any]:
        return super().get_context_data(**kwargs)


# *album views
class AlbumCreateView(LoginRequiredMixin, CreateView):
    """Представление создание альбома и треков которые в него входят."""

    model = Album
    template_name = "music/create_album.html"
    form_class = AlbumCreateForm
    success_url = "music:artist_detail"

    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        return render(
            request, self.template_name, {"album_form": AlbumCreateForm(), "track_formset": TrackInAlbumFormSet()}
        )

    def post(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> HttpResponse:
        print(request.POST)
