from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from dotenv import load_dotenv

from .services import TrackConvertorHLS

load_dotenv()


class TrackStream(View):
    def get(self, request: HttpRequest, track_id: int) -> HttpResponse:
        service = TrackConvertorHLS()
        a = service.convert_track(track_id)
        print(a)
