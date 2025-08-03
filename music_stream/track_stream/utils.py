import logging
import os
import subprocess
from datetime import timedelta

from dotenv import load_dotenv
from minio import Minio
from music.models import Track

logger = logging.getLogger(__name__)
load_dotenv()
client = Minio(
    endpoint=os.getenv("MINIO_STORAGE_ENDPOINT"),
    access_key=os.getenv("MINIO_STORAGE_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_STORAGE_SECRET_KEY"),
    secure=False,
)
bucket_name = "media"
import logging
import os
import tempfile

from dotenv import load_dotenv
from minio import Minio

logger = logging.getLogger(__name__)
load_dotenv()

# Инициализация клиента MinIO
minio_client = Minio(
    endpoint=os.getenv("MINIO_STORAGE_ENDPOINT"),
    access_key=os.getenv("MINIO_STORAGE_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_STORAGE_SECRET_KEY"),
    secure=False,
    region="us-east-1",  # Явное указание региона
)
BUCKET_NAME = "media"


def convert_track_to_hls(track_id: int) -> str:
    """Конвертирует трек в HLS формат и загружает в MinIO."""
    track = Track.objects.get(id=track_id)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Скачивание с оригинальным именем и расширением
            original_ext = os.path.splitext(track.audio_file.name)[1]
            input_file = os.path.join(temp_dir, f"original_audio{original_ext}")
            minio_client.fget_object(BUCKET_NAME, track.audio_file.name, input_file)

            # 2. Проверка скачанного файла
            if not os.path.exists(input_file):
                msg = f"File not downloaded: {input_file}"
                raise RuntimeError(msg)

            if os.path.getsize(input_file) == 0:
                msg = f"Empty file: {input_file}"
                raise RuntimeError(msg)

            # 3. Подготовка выходной директории
            output_dir = os.path.join(temp_dir, f"hls_{track_id}")
            os.makedirs(output_dir, exist_ok=True)

            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                input_file,
                "-c:a",
                "aac",
                "-b:a",
                "256k",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-f",
                "segment",
                "-segment_time",
                "6",
                "-segment_format",
                "mpegts",
                "-segment_list",
                os.path.join(output_dir, "playlist.m3u8"),
                "-segment_list_type",
                "m3u8",
                os.path.join(output_dir, "segment_%03d.ts"),
            ]
            # 5. Запуск с таймаутом (60 сек)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)

            # 6. Проверка результата
            if result.returncode != 0:
                error_msg = f"FFmpeg error ({result.returncode}): {result.stderr}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # 7. Проверка создания выходных файлов
            if not os.path.exists(os.path.join(output_dir, "playlist.m3u8")):
                msg = "HLS playlist not created"
                raise RuntimeError(msg)

            return upload_hls_to_minio(track_id, output_dir)

    except Exception as e:
        logger.exception(f"HLS conversion failed: {e!s}")
        raise


def upload_hls_to_minio(track_id: int, output_dir: str) -> str:
    """Загружает HLS файлы в MinIO и возвращает URL плейлиста."""
    minio_base_path = f"tracks/{track_id}/hls"

    # Загружаем все файлы в директории
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)

        # Определяем Content-Type
        content_type = "video/MP2T" if filename.endswith(".ts") else "application/vnd.apple.mpegurl"

        minio_client.fput_object(BUCKET_NAME, f"{minio_base_path}/{filename}", file_path, content_type=content_type)

    # Обновляем модель трека

    # Генерируем URL для плейлиста
    return minio_client.presigned_get_object(
        BUCKET_NAME, f"{minio_base_path}/playlist.m3u8", expires=timedelta(hours=1)
    )
