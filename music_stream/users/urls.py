from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("profile/<int:user_id>", views.ProfileDetailView.as_view(), name="profile"),
]
