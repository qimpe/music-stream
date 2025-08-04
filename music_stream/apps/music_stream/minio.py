import logging
import os
from datetime import timedelta

from django.conf import settings
from dotenv import load_dotenv
from minio import Minio

logger = logging.getLogger(__name__)
load_dotenv()


class MinioClient:
    def __init__(self) -> None:
        self.client = Minio(
            endpoint=os.getenv("MINIO_STORAGE_ENDPOINT", "localhost:9000"),
            access_key=os.getenv("MINIO_STORAGE_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_STORAGE_SECRET_KEY"),
            secure=False,
        )

    def fetch_presigned_track_hsl_playlist_url(self, object_name: str) -> str:
        """возвращает подписанный url плейлиста для трека."""
        return self.client.presigned_get_object(
            settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, object_name, expires=timedelta(minutes=15)
        )
