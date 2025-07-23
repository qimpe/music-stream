from django.contrib import admin

from .models import Album, AlbumArtist, Artist, Track, TrackInAlbum, TrackMetadata, UserArtist

# Register your models here.


class ArtistAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "bio", "image", "status", "balance"]
    list_filter = ["name", "slug", "status"]
    search_fields = ["name", "slug", "status"]
    prepopulated_fields = {"slug": ("name",)}


class TrackMetedataAdmin(admin.TabularInline):
    model = TrackMetadata


class TrackAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "cover",
        "audio_file",
        "is_explicit",
        "created_at",
        "release_date",
        "status",
    ]
    list_filter = ["status", "is_explicit"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TrackMetedataAdmin]


class AlbumAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "cover",
        "is_explicit",
        "created_at",
        "release_date",
        "status",
    ]
    list_filter = ["status", "is_explicit"]
    search_fields = ["title"]


class TrackInAlbumAdmin(admin.ModelAdmin): ...


admin.site.register(Track, TrackAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(TrackMetadata, TrackInAlbumAdmin)
admin.site.register(Album)
admin.site.register(TrackInAlbum)
admin.site.register(UserArtist)
admin.site.register(AlbumArtist)
