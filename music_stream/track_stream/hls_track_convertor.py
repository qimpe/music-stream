import os
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from music.models import Track
from music.services import TrackService

from music_stream.minio import MinioClient


class TrackConvertorHLS:
    """Конвертор треков в AAC и сегментация."""

    def convert_track(self, track_id: int) -> str:
        """Преобразует трек в сегменты для hls stream."""
        minio = MinioClient()
        service = TrackService()
        track = service.fetch_track_by_id(track_id)

        # * получаем расширение нужного файла
        # * создаем временный файл
        # * получаем оригинальный файл из minio и копируем его в temp_file
        output_dir_1 = Path("test_for_hls")
        Path.mkdir(output_dir_1, exist_ok=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(track.audio_file.name)
            audio_file_extension = path.suffix
            temp_file = str(Path(temp_dir, f"audio{audio_file_extension}"))
            minio.client.fget_object("media", track.audio_file.name, temp_file)
            output_dir = Path(temp_dir, f"hls_f{track_id}")
            Path.mkdir(output_dir)
            """cmd = [
                "ffmpeg",
                "-y",
                "-i",
                temp_file,
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
                "7",
                "-segment_format",
                "mpegts",
                "-segment_list",
                str(Path(output_dir, "playlist.m3u8")),
                "-segment_list_type",
                "m3u8",
                str(Path(output_dir, "segment_%03d.ts")),
            ]"""
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                temp_file,
                "-vn",  # Отключаем видео
                "-c:a",
                "aac",  # Кодек AAC (обязательно для HLS)
                "-b:a",
                "256k",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-f",
                "hls",
                "-hls_time",
                "7",  # Целевая длительность сегмента
                "-hls_list_size",
                "0",  # Все сегменты в плейлисте
                "-hls_flags",
                "single_file+independent_segments+append_list",  # Ключевые флаги
                "-hls_segment_type",
                "fmp4",  # Требуется для byte ranges
                "-hls_segment_filename",
                str(Path(output_dir, "audio.mp4")),  # Единый файл
                "-force_key_frames",
                "expr:gte(t,n_forced*7)",  # Принудительное разделение
                str(Path(output_dir, "playlist.m3u8")),
            ]
            subprocess.run(cmd, capture_output=True, text=True, check=False)

            return self._upload_hls_to_minio(track, output_dir)

    def _upload_hls_to_minio(self, track: Track, output_dir: Path) -> str:
        """Загружает HLS файлы в MinIO и возвращает URL плейлиста."""
        minio = MinioClient()
        minio_base_path = Path("tracks", str(track.pk), "hls")
        minio_base_path = f"tracks/{track.pk}/hls"
        # Загружаем все файлы в директории
        for filename in output_dir.iterdir():
            new_file_name = os.path.split(filename)[-1]
            file_path = str(Path(output_dir, filename))
            content_type = "video/MP2T" if filename.suffix == ".ts" else "application/vnd.apple.mpegurl"
            minio.client.fput_object(
                settings.MINIO_STORAGE_MEDIA_BUCKET_NAME,
                f"{minio_base_path}/{new_file_name}",
                file_path,
                content_type=content_type,
            )
        playlist_name = "playlist.m3u8"
        playlist_url = f"{minio_base_path}/{playlist_name}"
        print(playlist_url)
        print(22222222222222222222222222222)
        service = TrackService()
        service.update_track_hls_playlist_url(track.pk, playlist_url)
        return minio.fetch_presigned_track_hsl_playlist_url(playlist_url)
