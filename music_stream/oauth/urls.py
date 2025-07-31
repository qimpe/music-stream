from django.urls import path

from . import views

app_name = "oauth"


urlpatterns = [
    path("<str:provider>/", views.OAuthView.as_view(), name="oauth"),
    path("<str:provider>/callback/", views.OAuthCallback.as_view(), name="callback"),
]


"""
urlpatterns = [
    path("github/", views.GoogleOAuth.as_view(), name="github_oauth"),
    path("github/callback/", views.GoogleOAuthCallback.as_view(), name="github_auth_callback"),
    path("google/", views.GoogleOAuth.as_view(), name="google_oauth"),
    path("google/callback/", views.GoogleOAuthCallback.as_view(), name="google_auth_callback"),
]
"""
