import logging
from typing import Any

from django.http import HttpRequest

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> Any:
        logger.info(
            f"Request | METHOD - {request.method} | URI- {request.path} | USER - {request.user} | BODY - {request.body}"
        )
        response = self.get_response(request)
        logger.info(f"Response | STATUS - {response.status_code} | USER - {request.user} | BODY - {request.body}")
        return response
