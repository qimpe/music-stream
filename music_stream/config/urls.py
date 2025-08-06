from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path

handler404 = "apps.core.views.error_404"

urlpatterns = [
    path("", include("apps.music.urls")),
    path("admin/", admin.site.urls),
    path("users/", include("apps.users.urls")),
    path("oauth2/", include("apps.oauth.urls")),
    *debug_toolbar_urls(),
    path("__reload__/", include("django_browser_reload.urls")),
]
