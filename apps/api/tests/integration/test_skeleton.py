"""Phase B1 deliverables (TDD §9, §13.4)."""

from __future__ import annotations

import logging
from typing import Any, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_health_returns_ok_when_db_reachable(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_returns_503_when_db_unreachable(unhealthy_client: TestClient) -> None:
    response = unhealthy_client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy"}


def test_openapi_is_valid_3_1(client: TestClient) -> None:
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["openapi"].startswith("3.1")
    assert schema["info"]["title"] == "TaskFlow API"
    assert "/health" in schema["paths"]


def test_request_id_is_echoed_in_response_header(client: TestClient) -> None:
    incoming = "deadbeefcafebabe"
    response = client.get("/health", headers={"X-Request-Id": incoming})
    assert response.headers["X-Request-Id"] == incoming


def test_request_id_is_generated_when_missing(client: TestClient) -> None:
    response = client.get("/health")
    assert "X-Request-Id" in response.headers
    assert len(response.headers["X-Request-Id"]) >= 16


def test_validation_error_uses_envelope(
    app_with_test_routes: FastAPI,
    client: TestClient,
) -> None:
    # Wrong type (int instead of str) yields a per-field error at loc=("body", "title").
    response = client.post("/_test/echo", json={"title": 42})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["fields"]["title"] == ["INVALID_TYPE"]


def test_validation_error_required_code_for_missing_field(
    app_with_test_routes: FastAPI,
    client: TestClient,
) -> None:
    # Missing required field maps Pydantic `missing` → ADR 043 `REQUIRED`.
    response = client.post("/_test/echo", json={"other": "x"})
    assert response.status_code == 422
    body = response.json()
    assert body["error"]["fields"]["title"] == ["REQUIRED"]


def test_app_error_uses_envelope(
    app_with_test_routes: FastAPI,
    client: TestClient,
) -> None:
    response = client.get("/_test/not-found")
    assert response.status_code == 404
    body = response.json()
    assert body == {
        "error": {"code": "THING_NOT_FOUND", "message": "No such thing."},
    }


def test_permission_and_conflict_envelope(
    app_with_test_routes: FastAPI,
    client: TestClient,
) -> None:
    forbidden = client.get("/_test/forbidden")
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "NOT_ALLOWED"

    conflict = client.get("/_test/conflict")
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "DUP"


def test_unhandled_error_returns_500_envelope_and_logs(
    app_with_test_routes: FastAPI,
    client: TestClient,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.ERROR, logger="taskflow.request")
    response = client.get("/_test/explode", headers={"X-Request-Id": "test-trace"})
    assert response.status_code == 500
    body = response.json()
    assert body == {
        "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
    }
    # The middleware emits a single ERROR record per unhandled exception, with the
    # full request context (request_id, path, method, duration_ms) and traceback.
    matched = [
        r
        for r in caplog.records
        if r.name == "taskflow.request"
        and isinstance(r.msg, dict)
        and r.msg.get("event") == "request.error"
    ]
    assert matched, "expected a request.error log line at ERROR level"
    payload = cast(dict[str, Any], matched[0].msg)
    assert payload["level"] == "error"
    assert payload["status"] == 500
    assert payload["request_id"] == "test-trace"
    assert payload["path"] == "/_test/explode"
    assert payload["method"] == "GET"
    assert "exception" in payload  # traceback rendered by format_exc_info
