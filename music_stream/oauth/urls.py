from django.urls import path

from . import views

app_name = "oauth"


urlpatterns = [
    path("<str:provider>/", views.OAuthView.as_view(), name="oauth"),
    path("<str:provider>/callback/", views.OAuthCallback.as_view(), name="callback"),
]
