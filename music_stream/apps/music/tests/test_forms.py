import base64
from io import BytesIO

from django.core.files.uploadedfile import (InMemoryUploadedFile,
                                            SimpleUploadedFile)
from django.test import TestCase
from faker import Faker
from music.forms import AlbumForm, ArtistCreateForm


class AlbumCreateFormTest(TestCase):
    def setUp(self) -> None:
        self.fake = Faker()

    def create_test_image(self) -> bytes:
        """Возвращает байты валидного тестового изображения (1x1 PNG)."""
        return base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')

    
    
    
    def test_valid_form(self) -> None:
        """Тест с корректными данными."""
        test_image = self.create_test_image()
        image = InMemoryUploadedFile(
            BytesIO(test_image),
            field_name='cover',
            name='test_image.png',
            content_type='image/png',
            size=len(test_image),
            charset='utf-8',
        )
        form_data = {
            "title": self.fake.sentence(nb_words=3),
            "is_explicit": self.fake.boolean(),
            "genre":self.fake.word()
        }
        form = AlbumForm(data=form_data, files={"cover": image})
        self.assertTrue(form.is_valid())

    def test_valid_image_extensions(self) -> None:
        """Тест допустимых расширений изображений."""
        test_image = self.create_test_image()
        valid_extensions = ["jpg", "jpeg", "png", "webp"]
        for ext in valid_extensions:
            with self.subTest(ext=ext):
                if ext in ["jpg", "jpeg"]:
                    content_type = "image/jpeg"
                elif ext == "png":
                    content_type = "image/png"
                elif ext == "webp":
                    content_type = "image/webp"
                image = InMemoryUploadedFile(
                    BytesIO(test_image),
                    field_name='cover',
                    name=f"test_image.{ext}",
                    content_type=content_type,
                    size=len(test_image),
                    charset='utf-8',
                )
                form_data = {
                    "title": self.fake.sentence(nb_words=3),
                    "is_explicit": self.fake.boolean(),
                    "genre":self.fake.word()
                }
                form = AlbumForm(data=form_data, files={"cover": image})
                self.assertTrue(form.is_valid())

    def test_invalid_image_extensions(self) -> None:
        """Тест недопустимых расширений файлов."""
        test_image = self.create_test_image()
        invalid_extensions = ["bmp", "tiff", "svg", "txt", "pdf", "doc", "exe", "gif"]
        for ext in invalid_extensions:
            with self.subTest(ext=ext):
                content_type = "image/jpeg"
                image = InMemoryUploadedFile(
                    BytesIO(test_image),
                    field_name='cover',
                    name=f"test_image.{ext}",
                    content_type=content_type,
                    size=len(test_image),
                    charset='utf-8',
                )
                form_data = {
                    "title": self.fake.sentence(nb_words=3),
                    "is_explicit": self.fake.boolean(),
                }
                form = AlbumForm(data=form_data, files={"cover": image})
                self.assertFalse(form.is_valid())
                self.assertIn("cover", form.errors)
                self.assertIn("File extension", str(form.errors["cover"][0]))

    def test_no_image_provided(self) -> None:
        """Тест на отсутствие изображения."""
        form_data = {
            "title": self.fake.sentence(nb_words=3),
            "is_explicit": self.fake.boolean(),
        }
        form = AlbumForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("cover", form.errors)
        self.assertIn("This field is required.", str(form.errors["cover"][0]))

    def test_invalid_image_content(self) -> None:
        """Тест на невалидное содержимое изображения."""
        invalid_image = SimpleUploadedFile(
            name='test.txt',
            content=b'not an image',
            content_type='text/plain',
        )
        form_data = {
            "title": self.fake.sentence(nb_words=3),
            "is_explicit": self.fake.boolean(),
        }
        form = AlbumForm(data=form_data, files={"cover": invalid_image})
        self.assertFalse(form.is_valid())
        self.assertIn("cover", form.errors)
        self.assertIn("Upload a valid image", str(form.errors["cover"][0]))

class ArtistCreateFormTest(TestCase):
    def setUp(self) -> None:
        self.fake = Faker()

    def create_test_image(self) -> bytes:
        """Возвращает байты валидного тестового изображения (1x1 PNG)."""
        return base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')

    def test_clean_image(self):
        test_image=self.create_test_image()
        image = InMemoryUploadedFile(
            BytesIO(test_image),
            field_name="image",
            name="test_image.png",
            content_type="image/png",
            size=len(test_image),
            charset="utf-8",
        )
        form_data = {"name": self.fake.word(), "bio": self.fake.text()}
        form = ArtistCreateForm(data=form_data, files={"image": image})
        self.assertTrue(form.is_valid())
        
    
    def test_valid_image(self) -> None:
        """Тест на валидность изображения."""
        test_image = self.create_test_image()
        image = InMemoryUploadedFile(
            BytesIO(test_image),
            field_name="image",
            name="test_image.png",
            content_type="image/png",
            size=len(test_image),
            charset="utf-8",
        )
        form_data = {"name": self.fake.word(), "bio": self.fake.text()}
        form = ArtistCreateForm(data=form_data, files={"image": image})
        self.assertTrue(form.is_valid())

    def test_valid_extensions(self) -> None:
        """Тест на валидность расширения."""
        test_image = self.create_test_image()
        valid_extensions = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
        for ext, ext_content_type in valid_extensions.items():
            with self.subTest(ext=ext):
                image = InMemoryUploadedFile(
                    BytesIO(test_image),
                    field_name="image",
                    name=f"test_image.{ext}",
                    content_type=ext_content_type,
                    size=len(test_image),
                    charset="utf-8",
                )
                form_data = {"name": self.fake.word(), "bio": self.fake.text()}
                form = ArtistCreateForm(data=form_data, files={"image": image})
                self.assertTrue(form.is_valid())

    def test_invalid_extensions(self) -> None:
        """Тест на невалидные расширения."""
        test_image = self.create_test_image()
        invalid_extensions = {"tiff": "image/tiff", "gif": "image/gif", "bmp": "image/bmp", "svg": "image/svg"}
        for ext, ext_content_type in invalid_extensions.items():
            with self.subTest(ext=ext):
                image = InMemoryUploadedFile(
                    BytesIO(test_image),
                    field_name="image",
                    name=f"test_image.{ext}",
                    content_type=ext_content_type,
                    size=len(test_image),
                    charset="utf-8",
                )
                form_data = {"name": self.fake.word(), "bio": self.fake.text()}
                form = ArtistCreateForm(data=form_data, files={"image": image})
                self.assertFalse(form.is_valid())

    def test_no_image_provided(self) -> None:
        """Тест на отсутствие изображения."""
        form_data = {"name": self.fake.word(), "bio": self.fake.text()}
        form = ArtistCreateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)
        self.assertIn("This field is required.", str(form.errors["image"][0]))

    def test_invalid_image_content(self) -> None:
        """Тест на невалидное содержимое изображения."""
        invalid_image = SimpleUploadedFile(
            name='test.txt',
            content=b'not an image',
            content_type='text/plain',
        )
        form_data = {"name": self.fake.word(), "bio": self.fake.text()}
        form = ArtistCreateForm(data=form_data, files={"image": invalid_image})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)
        self.assertIn("Upload a valid image", str(form.errors["image"][0]))