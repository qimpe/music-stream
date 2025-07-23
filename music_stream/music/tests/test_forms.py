import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from faker import Faker
from PIL import Image

from music.forms import AlbumCreateForm, ArtistCreateForm


class AlbumCreateFormTest(TestCase):
    def setUp(self) -> None:
        self.fake = Faker()
        self.required_fields = ["title", "cover"]

    def create_test_image(self, format="JPEG") -> bytes:
        """Создает валидное тестовое изображение в памяти."""
        image = io.BytesIO()
        img = Image.new("RGB", (100, 100), color="red")
        img.save(image, format=format)
        return image.getvalue()

    def test_valid_form(self) -> None:
        """Тест с корректными данными."""
        # Создаем валидное изображение
        image_bytes = self.create_test_image(format="JPEG")

        uploaded_image = SimpleUploadedFile(
            name="test_image.jpg",
            content=image_bytes,
            content_type="image/jpeg",
        )

        form_data = {
            "title": self.fake.sentence(nb_words=3),
            "is_explicit": self.fake.boolean(),
        }
        form_files = {"cover": uploaded_image}

        form = AlbumCreateForm(data=form_data, files=form_files)
        assert form.is_valid(), f"Ошибки валидации: {form.errors}"

    def test_valid_image_extensions(self) -> None:
        """Тест допустимых расширений изображений."""
        valid_extensions = ["jpg", "jpeg", "png", "webp"]
        for ext in valid_extensions:
            with self.subTest(ext=ext):
                if ext in ["jpg", "jpeg"]:
                    file_format = "JPEG"
                    content_type = "image/jpeg"
                elif ext == "png":
                    file_format = "PNG"
                    content_type = "image/png"
                elif ext == "webp":
                    file_format = "WEBP"
                    content_type = "image/webp"

                image_bytes = self.create_test_image(format=file_format)

                uploaded_image = SimpleUploadedFile(
                    name=f"test_image.{ext}",
                    content=image_bytes,
                    content_type=content_type,
                )

                form_data = {
                    "title": self.fake.sentence(nb_words=3),
                    "is_explicit": self.fake.boolean(),
                }
                form_files = {"cover": uploaded_image}

                form = AlbumCreateForm(data=form_data, files=form_files)
                assert form.is_valid(), f"Ошибка для расширения .{ext}: {form.errors}"

    def test_invalid_image_extensions(self) -> None:
        """Тест недопустимых расширений файлов."""
        invalid_extensions = ["bmp", "tiff", "svg", "txt", "pdf", "doc", "exe", "gif"]

        for ext in invalid_extensions:
            with self.subTest(ext=ext):
                # Создаем валидное JPEG изображение, но с недопустимым расширением
                image_bytes = self.create_test_image(format="JPEG")

                uploaded_image = SimpleUploadedFile(
                    name=f"test_image.{ext}",
                    content=image_bytes,
                    content_type="image/jpeg",  # Content-Type не соответствует расширению
                )

                form_data = {
                    "title": self.fake.sentence(nb_words=3),
                    "is_explicit": self.fake.boolean(),
                }
                form_files = {"cover": uploaded_image}

                form = AlbumCreateForm(data=form_data, files=form_files)
                assert not form.is_valid(), f"Форма должна быть невалидной для расширения .{ext}"
                assert "cover" in form.errors
                assert "File extension" in form.errors["cover"][0], f"Неправильное сообщение об ошибке для .{ext}"


class ArtistCreateFormTest(TestCase):
    """Форма создания Артиста."""

    def setUp(self) -> None:
        self.fake = Faker()
        self.required_fields = ["title", "cover"]

    def test_valid_form(self) -> None:
        form_data = {"title": self.fake.word, "bio": self.fake.text}
        ArtistCreateForm(data=form_data)
