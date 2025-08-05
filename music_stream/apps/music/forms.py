from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.forms import inlineformset_factory
from django_stubs_ext.db.models import TypedModelMeta

from .models import Album, Artist, Track, TrackInAlbum


class ArtistCreateForm(forms.ModelForm):
    """Форма создания Артиста."""

    name = forms.fields.CharField(required=True)
    image = forms.ImageField(
        required=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
        ],
        help_text="Допустимые форматы: JPG, JPEG, PNG, WEBP. Макс. размер: 5 МБ.",
    )

    def clean_image(self) -> None:
        image = self.cleaned_data.get("image")
        if image:
            max_height = 2000
            max_width = 2000
            if image.image.width > max_width or image.image.height > max_height:
                msg = "Превышен максимальны размер фото"
                raise ValidationError(msg)
            return image
        msg = "Фото не загружено"
        raise ValidationError(msg)

    class Meta(TypedModelMeta):
        model = Artist
        fields = ["name", "image", "bio"]


class AlbumForm(forms.ModelForm):
    """Форма создания Альбома."""

    title = forms.CharField(required=True)
    cover = forms.ImageField(
        required=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
        ],
        help_text="Допустимые форматы: JPG, JPEG, PNG, WEBP. Макс. размер: 5 МБ.",
    )
    genre = forms.CharField()

    class Meta(TypedModelMeta):
        model = Album
        fields = ["title", "cover", "is_explicit"]


class TrackCreateForm(forms.ModelForm):
    """Форма создания трека."""

    audio_file = forms.FileField(
        validators=[
            FileExtensionValidator(allowed_extensions=["mp3", "wav", "flac"]),
        ],
    )

    class Meta(TypedModelMeta):
        model = Track
        fields = ["title", "audio_file", "is_explicit"]


class TrackInAlbumForm(forms.ModelForm):
    track_title = forms.CharField(max_length=255, label="Название трека", required=True)
    is_explicit = forms.BooleanField(required=False)
    audio_file = forms.FileField(
        required=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["mp3", "wav", "flac"]),
        ],
    )
    position = forms.IntegerField(
        required=True,
        min_value=1,  # Устанавливаем минимальное значение
        label="Позиция",
        help_text="Позиция трека в альбоме (начиная c 1)",
        initial=1,
    )
    genre = forms.CharField(max_length=50)

    class Meta:
        model = TrackInAlbum
        fields = ["position", "genre"]

    def clean_position(self) -> int:
        position = self.cleaned_data.get("position")
        if position and position >= 1:
            return position
        msg = "Позиция должна быть положительной"
        raise forms.ValidationError(msg)

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        track_title = cleaned_data.get("track_title")
        audio_file = cleaned_data.get("audio_file")
        if not track_title and not audio_file:
            msg = "Название трека и аудиофайл не могут быть одновременно пустыми."
            raise forms.ValidationError(msg)
        return cleaned_data


TrackInAlbumFormSet = inlineformset_factory(
    Album,
    TrackInAlbum,
    form=TrackInAlbumForm,
    min_num=1,
    extra=0,
    validate_min=True,
    can_delete=False,
)
