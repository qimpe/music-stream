from django.test import TestCase, override_settings
from django.urls import reverse
from music.models import Artist

from .factories import ArtistFactory, UserFactory


class IndexViewTest(TestCase):
    def test_index_view(self) -> None:
        """Тест представления главной страницы."""
        url = reverse("music:index")
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertTemplateUsed(response, "index.html")


class ArtistCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.url = reverse("music:create_artist")

    @override_settings(DEBUG=True)
    def test_artist_create_view(self) -> None:
        """Тест представления по созданию карточки артиста."""
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertTemplateUsed(response, "music/create_artist.html")

        # POST-запрос с данными
        artist = ArtistFactory.build()  # build() вместо create() - не сохраняет в БД
        response = self.client.post(
            self.url,
            {
                "name": artist.name,
                "bio": artist.bio,
                "image": artist.image,  # Используем SimpleUploadedFile
            },
        )
        assert Artist.objects.count() == 1
        assert response.status_code == 302


class ArtistDetailViewTest(TestCase):
    def setUp(self) -> None:
        self.artist = ArtistFactory()
        self.url = reverse("music:artist_detail", kwargs={"artist_id": self.artist.id})

    def test_artist_detail_view(self) -> None:
        """Тест представления карточки артиста."""
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert self.assertTemplateUsed("music/artist_detail.html")
        assert "artist" in response.context  # Стандартное имя для DetailView
        assert response.context["artist"].id == self.artist.id
        self.assertContains(response, self.artist.name)
        assert "artist_albums" in response.context
        assert "releases" in response.context
