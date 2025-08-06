from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# Create your views here.
def error_404(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "apps/errors/404.html", status=404)
