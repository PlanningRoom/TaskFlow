"""Global error contract per ADR 043 / TDD §9.2.

Every error response is the envelope:
    { "error": { "code": str, "message": str, "fields"?: { name: [code, ...] } } }

Field codes are stable, machine-readable strings. The frontend keys translated
copy off them (Decision 018), so they must not drift.
"""

from __future__ import annotations

from typing import Any, Final

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Pydantic v2 error type → canonical ADR 043 code.
# When extending, prefer existing codes over new ones; document additions in ADR 043.
_PYDANTIC_TYPE_TO_CODE: Final[dict[str, str]] = {
    "missing": "REQUIRED",
    "string_type": "INVALID_TYPE",
    "int_type": "INVALID_TYPE",
    "float_type": "INVALID_TYPE",
    "bool_type": "INVALID_TYPE",
    "dict_type": "INVALID_TYPE",
    "list_type": "INVALID_TYPE",
    "json_invalid": "INVALID_JSON",
    "json_type": "INVALID_JSON",
    "string_too_short": "TOO_SHORT",
    "string_too_long": "TOO_LONG",
    "value_error": "INVALID",
    "string_pattern_mismatch": "INVALID_FORMAT",
    "enum": "INVALID_CHOICE",
    "literal_error": "INVALID_CHOICE",
    "url_parsing": "INVALID_URL",
    "url_scheme": "INVALID_URL",
    "uuid_parsing": "INVALID_UUID",
    "uuid_type": "INVALID_UUID",
    "uuid_version": "INVALID_UUID",
    "datetime_parsing": "INVALID_DATETIME",
    "datetime_type": "INVALID_DATETIME",
    "date_parsing": "INVALID_DATE",
    "date_type": "INVALID_DATE",
    "int_parsing": "INVALID_TYPE",
    "float_parsing": "INVALID_TYPE",
    "bool_parsing": "INVALID_TYPE",
    "greater_than": "OUT_OF_RANGE",
    "greater_than_equal": "OUT_OF_RANGE",
    "less_than": "OUT_OF_RANGE",
    "less_than_equal": "OUT_OF_RANGE",
    "multiple_of": "OUT_OF_RANGE",
    "finite_number": "OUT_OF_RANGE",
    "missing_argument": "REQUIRED",
    "value_required": "REQUIRED",
}


def _canonical_field_code(pydantic_type: str) -> str:
    """Map a Pydantic v2 error `type` string to an ADR 043 canonical code."""
    if pydantic_type in _PYDANTIC_TYPE_TO_CODE:
        return _PYDANTIC_TYPE_TO_CODE[pydantic_type]
    # Common suffix patterns we haven't enumerated explicitly.
    if pydantic_type.endswith("_parsing") or pydantic_type.endswith("_type"):
        return "INVALID_TYPE"
    if pydantic_type.startswith("string_"):
        return "INVALID_FORMAT"
    return pydantic_type.upper()


class AppError(Exception):
    """Base for application-level exceptions surfaced to clients."""

    code: str = "APP_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        fields: dict[str, list[str]] | None = None,
    ) -> None:
        self.message = message
        if code is not None:
            self.code = code
        self.fields = fields
        super().__init__(message)


class NotFoundError(AppError):
    code = "NOT_FOUND"
    status_code = 404


class PermissionDeniedError(AppError):
    code = "PERMISSION_DENIED"
    status_code = 403


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = 409


class RateLimitedError(AppError):
    code = "RATE_LIMITED"
    status_code = 429

    def __init__(
        self,
        message: str = "Too many requests.",
        *,
        retry_after: int | None = None,
        code: str | None = None,
    ) -> None:
        super().__init__(message, code=code)
        self.retry_after = retry_after


def _envelope(
    code: str,
    message: str,
    fields: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if fields is not None:
        error["fields"] = fields
    return {"error": error}


async def app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    headers: dict[str, str] = {}
    if isinstance(exc, RateLimitedError) and exc.retry_after is not None:
        headers["Retry-After"] = str(exc.retry_after)
    return JSONResponse(
        _envelope(exc.code, exc.message, exc.fields),
        status_code=exc.status_code,
        headers=headers or None,
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    fields: dict[str, list[str]] = {}
    for err in exc.errors():
        loc = err.get("loc", ())
        # loc is e.g. ("body", "title") — drop the source segment for the field name.
        path = [str(p) for p in loc[1:]] if len(loc) > 1 else [str(p) for p in loc]
        if not path:
            continue
        field = ".".join(path)
        code = _canonical_field_code(str(err.get("type", "invalid")))
        fields.setdefault(field, []).append(code)
    return JSONResponse(
        _envelope("VALIDATION_ERROR", "Validation failed.", fields),
        status_code=422,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    # No log here — the request middleware already logged the exception with full
    # request context (request_id, path, method, duration_ms, traceback).
    return JSONResponse(
        _envelope("INTERNAL_ERROR", "An unexpected error occurred."),
        status_code=500,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
