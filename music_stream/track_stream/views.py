from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from dotenv import load_dotenv

from .hls_track_convertor import TrackConvertorHLS

load_dotenv()


class TrackStream(View):
    def get(self, request: HttpRequest, track_id: int) -> HttpResponse:
        # a = convert_track_to_hls(track_id)
        # print(a)
        service = TrackConvertorHLS()
        a = service.convert_track(track_id)
        print(a)
        # return redirect(reverse_lazy("music:index"))
