import factory
from django.contrib.auth.models import User
from faker.providers import BaseProvider

from music.models import Artist, UserArtist


class StatusProvider(BaseProvider):
    def artist_status(self):
        return self.random_choices


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:  # type: ignore
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")


class ArtistFactory(factory.django.DjangoModelFactory):
    class Meta:  # type: ignore
        model = Artist

    name = factory.Faker("user_name")
    bio = factory.Faker("text")


class UsersArtistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserArtist

    user = factory.SubFactory(UserFactory)
    artist = factory.SubFactory(ArtistFactory)
