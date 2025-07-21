from django.contrib import admin

from .models import Artist, Track


# Register your models here.
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


class ArtistAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "bio", "image", "status", "balance"]
    list_filter = ["name", "slug", "status"]
    search_fields = ["name", "slug", "status"]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Track, TrackAdmin)
admin.site.register(Artist, ArtistAdmin)
