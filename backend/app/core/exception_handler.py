from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """Base class for all domain-level errors that map to an HTTP response.

    Attributes:
        status_code: HTTP status code to return.
        detail: Human-readable message placed in ``{"detail": ...}``.
    """

    status_code: int = 400
    detail: str = "Domain error"

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(detail or self.detail)
        if detail is not None:
            self.detail = detail


class NotFoundError(DomainError):
    status_code = 404
    detail = "Resource not found"


class ForbiddenError(DomainError):
    status_code = 403
    detail = "Forbidden"


class ConflictError(DomainError):
    status_code = 409
    detail = "Conflict"


class ValidationError(DomainError):
    status_code = 422
    detail = "Validation error"


class UnauthorizedError(DomainError):
    status_code = 401
    detail = "Unauthorized"


def register_exception_handlers(app: FastAPI) -> None:
    """Register the global handler that maps ``DomainError`` to HTTP responses."""

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        if (
            isinstance(exc, UnauthorizedError)
            and hasattr(exc, "token_type")
            and exc.token_type == "access"  # type: ignore
        ):
            headers = {"WWW-Authenticate": "Bearer"}
        else:
            headers = None

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=headers,
        )
