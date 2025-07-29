import typing

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django_stubs_ext.db.models import TypedModelMeta


# Create your models here.
class Status(models.TextChoices):
    ACTIVE = ("active", "Активен")
    CREATED = ("created", "Создан")
    PENDING = ("in_pending", "На рассмотрении")
    REJECTED = ("rejected", "Отклонен")
    DELETED = ("deleted", "Удален")


class Music(models.Model):
    title = models.CharField(null=False, blank=False, max_length=128, verbose_name="Название")
    slug = models.SlugField(null=False, max_length=128, unique=False)
    is_explicit = models.BooleanField(blank=True, null=False, default=False, verbose_name="Возрастное ограничение 18+")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta(TypedModelMeta):
        abstract = True

    def __str__(self) -> str:
        return self.title

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Artist(models.Model):
    name = models.CharField(null=False, blank=False, max_length=128, unique=True, verbose_name="Имя")
    slug = models.SlugField(null=False, max_length=128, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to="artists_images/", verbose_name="Фото")
    bio = models.TextField(default="", blank=True, verbose_name="Биография")
    status = models.CharField(
        max_length=15, choices=Status.choices, null=False, default=Status.CREATED, verbose_name="Статус"
    )

    balance = models.IntegerField(default=0, null=False, verbose_name="Баланс")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(TypedModelMeta):
        indexes = [
            models.Index(fields=["name"], name="idx_artist_name"),
            models.Index(fields=["slug"], name="idx_artist_slug"),
            models.Index(fields=["status"], name="idx_artist_status"),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Genre(models.Model):
    title = models.CharField(null=False, blank=False, max_length=128, unique=True)
    slug = models.SlugField(null=False, max_length=128)
    description = models.TextField()
    origin_country = models.CharField(max_length=100, null=False)
    decade_emerged = models.PositiveSmallIntegerField()
    min_bpm = models.PositiveSmallIntegerField(null=True, blank=True)
    max_bpm = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta(TypedModelMeta):
        indexes = [
            models.Index(fields=["title"], name="idx_genre_title"),
            models.Index(fields=["slug"], name="idx_genre_slug"),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Album(Music):
    cover = models.ImageField(upload_to="music_covers/", verbose_name="Обложка")
    release_date = models.DateTimeField(null=True, verbose_name="Дата релиза")
    status = models.CharField(
        max_length=15, choices=Status.choices, null=False, default=Status.PENDING, verbose_name="Статус"
    )

    class Meta(TypedModelMeta):  # type: ignore[assignment]
        indexes = [
            models.Index(fields=["title"], name="idx_album_title"),
            models.Index(fields=["slug"], name="idx_album_slug"),
        ]


class Track(Music):
    cover = models.ImageField(upload_to="music_covers/", verbose_name="Обложка")
    audio_file = models.FileField(upload_to="tracks/")
    release_date = models.DateTimeField(null=True, verbose_name="Дата релиза")
    status = models.CharField(
        max_length=15, choices=Status.choices, null=False, default=Status.PENDING, verbose_name="Статус"
    )

    class Meta(TypedModelMeta):  # type: ignore[assignment]
        indexes = [
            models.Index(fields=["title"], name="idx_track_title"),
            models.Index(fields=["slug"], name="idx_track_slug"),
        ]

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().save(*args, **kwargs)


class Playlist(Music):
    title = models.CharField(
        null=False, blank=False, max_length=128, unique=True, verbose_name="Мне нравится", default="favorite"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")
    cover = models.ImageField(upload_to="playlists_covers/", verbose_name="Обложка")

    class Meta(TypedModelMeta):  # type: ignore[assignment]
        unique_together = ("owner", "title")
        indexes = [
            models.Index(fields=["title"], name="idx_playlist_title"),
            models.Index(fields=["slug"], name="idx_playlist_slug"),
        ]


# Связные таблица


class AlbumArtist(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)

    class Meta(TypedModelMeta):
        unique_together = ("artist", "album")

    def __str__(self) -> str:
        return f"Artist {self.artist} manage album {self.album}"


class TrackMetadata(models.Model):
    track = models.OneToOneField(Track, on_delete=models.CASCADE)
    duration = models.PositiveSmallIntegerField()
    bitrate = models.PositiveSmallIntegerField()
    file_size = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"Metadata of {self.track}"


class TrackInPlaylist(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)

    class Meta(TypedModelMeta):
        unique_together = ("track", "playlist")

    def __str__(self) -> str:
        return f" Track {self.track} consist in {self.playlist}"


class TrackInAlbum(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(default=1, null=False, blank=False)

    class Meta(TypedModelMeta):
        ordering = ["position"]
        unique_together = ("track", "album")

    def __str__(self) -> str:
        return f" Track {self.track} consist in {self.album}"


class TrackGenres(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)

    class Meta(TypedModelMeta):
        unique_together = ("track", "genre")

    def __str__(self) -> str:
        return f" Track {self.track} has {self.genre} genre"


class AlbumGenres(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta(TypedModelMeta):
        unique_together = ("genre", "album")

    def __str__(self) -> str:
        return f"Album {self.album} has {self.genre} genre"


class PlaylistGenres(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta(TypedModelMeta):
        unique_together = ("playlist", "genre")

    def __str__(self) -> str:
        return f"Playlist {self.playlist} has {self.genre} genre"


class ArtistTrack(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Artist {self.artist} has {self.track} track"
