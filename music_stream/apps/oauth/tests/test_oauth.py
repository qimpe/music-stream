from django.test import TestCase
from faker import Faker
from oauth.oauth_config import (GithubOAuthFactory, GoogleOAuthFactory,
                                OAuthFactory, OAuthProvider)


class OAuthTest(TestCase):
    def setUp(self) -> None:
        self.fake = Faker()
        
    def create_oauth_provider_test(self,provider:OAuthProvider):
        """Тестирует создание провайдера"""
        factories: dict[OAuthProvider, type[OAuthFactory]] = {
            "google": GoogleOAuthFactory,
            "github": GithubOAuthFactory,
        }
        factory=OAuthFactory.fetch_oauth_provider(provider)
        assert isinstance(factory,GoogleOAuthFactory)
        assert isinstance(factory,GithubOAuthFactory)
        if provider not in factories.keys():
            new_provider=self.fake.word()
            assert not isinstance(factory,GoogleOAuthFactory)
            assert not isinstance(factory,GithubOAuthFactory)
            factory=OAuthFactory.fetch_oauth_provider(new_provider)
            assert not isinstance(factory,GoogleOAuthFactory)
            assert not isinstance(factory,GithubOAuthFactory)
            assert not isinstance(factory,OAuthFactory)
    