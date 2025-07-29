from django.contrib import admin

from .models import Album, AlbumArtist, AlbumGenres, Artist, Genre, Track, TrackGenres, TrackInAlbum, TrackMetadata

# Register your models here.


class ArtistAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "bio", "image", "status", "balance"]
    list_filter = ["name", "slug", "status"]
    search_fields = ["name", "slug", "status"]
    prepopulated_fields = {"slug": ("name",)}


class TrackMetadataAdminInline(admin.TabularInline):
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
    inlines = [TrackMetadataAdminInline]


class TrackInAlbumAdminInline(admin.TabularInline):
    model = TrackInAlbum


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
    inlines = [TrackInAlbumAdminInline]


admin.site.register(Track, TrackAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(TrackMetadata)
admin.site.register(TrackInAlbum)

admin.site.register(AlbumArtist)
admin.site.register(Genre)
admin.site.register(AlbumGenres)
admin.site.register(TrackGenres)
