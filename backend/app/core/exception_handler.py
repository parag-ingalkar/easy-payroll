from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Base class for all domain-level errors that map to an HTTP response.

    Attributes:
        status_code: HTTP status code to return.
        code: Stable machine-readable error code for API consumers.
        detail: Human-readable, client-safe message placed in ``{"detail": ...}``.
        context: Internal diagnostic data (ids, dates, etc.) - logged, never returned to the client.
    """

    status_code: int = 400
    code: str = "domain_error"
    detail: str = "Domain error"

    def __init__(self, detail: str | None = None, **context: object) -> None:
        super().__init__(detail or self.detail)
        if detail is not None:
            self.detail = detail
        self.context = context


class NotFoundError(DomainError):
    status_code = 404
    code = "not_found"
    detail = "Resource not found"


class ForbiddenError(DomainError):
    status_code = 403
    code = "forbidden"
    detail = "Forbidden"


class ConflictError(DomainError):
    status_code = 409
    code = "conflict"
    detail = "Conflict"


class ValidationError(DomainError):
    status_code = 422
    code = "validation_error"
    detail = "Validation error"


class UnauthorizedError(DomainError):
    status_code = 401
    code = "unauthorized"
    detail = "Unauthorized"
    token_type: str | None = None


def register_exception_handlers(app: FastAPI) -> None:
    """Register global handlers that map DomainError (and unhandled errors) to HTTP responses."""

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        if exc.context:
            logger.info("%s: %s", type(exc).__name__, exc.context)

        headers = None
        if isinstance(exc, UnauthorizedError) and exc.token_type == "access":
            headers = {"WWW-Authenticate": "Bearer"}

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "code": "internal_error"},
        )
