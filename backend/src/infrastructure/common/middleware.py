"""ASGI middleware: request ids, access logging and security headers.

Both are pure ASGI middleware, not ``BaseHTTPMiddleware``: wrapping the body
through ``BaseHTTPMiddleware`` truncates ``FileResponse`` and ``StaticFiles``
bodies, which breaks serving the built frontend.
"""

import time
import uuid

import structlog
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = structlog.get_logger(__name__)


class RequestIdAndLoggingMiddleware:
    """Give every request an id, bind it to the log context and log the outcome."""

    def __init__(self, app: ASGIApp, api_prefix: str) -> None:
        self.app = app
        self.api_prefix = api_prefix

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        path: str = scope.get("path", "")
        start = time.perf_counter()
        status_code = 500

        async def wrapped_send(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                MutableHeaders(raw=message["headers"])["X-Request-ID"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        finally:
            # Static asset requests would drown the API traffic in the log.
            if path.startswith(self.api_prefix) or status_code >= 500:  # noqa: PLR2004
                logger.info(
                    "request_completed",
                    method=scope.get("method"),
                    path=path,
                    status_code=status_code,
                    duration_ms=round((time.perf_counter() - start) * 1000, 2),
                )


class SecurityHeadersMiddleware:
    """Add baseline security headers to every response."""

    def __init__(self, app: ASGIApp, production: bool) -> None:
        self.app = app
        self.production = production

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def wrapped_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(raw=message["headers"])
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
                if self.production:
                    headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            await send(message)

        await self.app(scope, receive, wrapped_send)
