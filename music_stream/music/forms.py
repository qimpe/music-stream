from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import inlineformset_factory
from django_stubs_ext.db.models import TypedModelMeta

from .models import Album, Artist, Track, TrackInAlbum


class ArtistCreateForm(forms.ModelForm):
    """Форма создания Артиста."""

    class Meta(TypedModelMeta):
        model = Artist
        fields = ["name", "image", "bio"]


class AlbumCreateForm(forms.ModelForm):
    """Форма создания Альбома."""

    cover = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
        ],
        help_text="Допустимые форматы: JPG, JPEG, PNG, WEBP. Макс. размер: 5 МБ.",
    )

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
    # Поля для создания нового трека
    track_title = forms.CharField(max_length=255, label="Название трека")
    is_explicit = forms.BooleanField()
    audio_file = forms.FileField(
        validators=[
            FileExtensionValidator(allowed_extensions=["mp3", "wav", "flac"]),
        ],
    )

    class Meta:
        model = TrackInAlbum
        fields = ["position"]

    def clean_position(self) -> int:
        position = self.cleaned_data.get("position")
        if position and position > 1:
            return position
        msg = "Позиция должна быть положительной"
        raise forms.ValidationError(msg)


TrackInAlbumFormSet = inlineformset_factory(
    Album,
    TrackInAlbum,
    form=TrackInAlbumForm,
    extra=1,
    min_num=1,
    validate_min=True,
)
