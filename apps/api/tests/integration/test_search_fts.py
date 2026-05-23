"""Phase E3 — FTS edge cases (websearch_to_tsquery operators, malformed input).

Pins the Postgres FTS contract: malformed user input must never produce a
500, operator syntax behaves the way ADR 062 expects, and length-bombed
queries don't trip a server error.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from taskflow.settings import settings
from tests.integration._helpers import csrf_headers, signup_owner

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def app(db_engine: None) -> FastAPI:
    settings.cookie_secure = False
    from taskflow.main import app as fastapi_app

    return fastapi_app


@pytest.fixture
async def http(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


async def _seed(http: AsyncClient) -> None:
    await signup_owner(http)
    headers = csrf_headers(http)
    pid = (await http.post("/api/v1/projects", json={"name": "FTS"}, headers=headers)).json()["id"]
    for title, desc in [
        ("Sprint planning review", "review of sprint plan"),
        ("Sprint planning", "kick off the sprint"),
        ("Reviewing pull requests", "code review work"),
    ]:
        await http.post(
            f"/api/v1/projects/{pid}/tasks",
            json={"title": title, "description": desc},
            headers=headers,
        )


@pytest.mark.parametrize(
    "query",
    [
        "&",
        "&&",
        "|",
        '"unclosed quote',
        '""',
        "  ",
        ")",
        "()",
    ],
)
async def test_malformed_query_returns_empty_not_500(http: AsyncClient, query: str) -> None:
    await _seed(http)
    r = await http.get("/api/v1/search", params={"q": query})
    assert r.status_code == 200, r.text
    assert isinstance(r.json()["results"], list)


async def test_and_operator(http: AsyncClient) -> None:
    await _seed(http)
    r = await http.get("/api/v1/search", params={"q": "sprint AND review"})
    titles = {res["title"] for res in r.json()["results"]}
    # "AND" requires both — "Sprint planning" alone shouldn't match.
    assert "Sprint planning review" in titles
    assert "Sprint planning" not in titles


async def test_or_operator(http: AsyncClient) -> None:
    await _seed(http)
    r = await http.get("/api/v1/search", params={"q": "sprint OR pull"})
    titles = {res["title"] for res in r.json()["results"]}
    assert "Sprint planning review" in titles
    assert "Sprint planning" in titles
    assert "Reviewing pull requests" in titles


async def test_stemming_matches_inflected_forms(http: AsyncClient) -> None:
    await _seed(http)
    # English stemmer: "reviewing" → "review"; "review" matches "reviewing".
    r = await http.get("/api/v1/search", params={"q": "reviewing"})
    titles = {res["title"] for res in r.json()["results"]}
    assert "Sprint planning review" in titles
    assert "Reviewing pull requests" in titles


async def test_extreme_length_query_no_500(http: AsyncClient) -> None:
    await _seed(http)
    r = await http.get("/api/v1/search", params={"q": "a " * 2500})
    assert r.status_code == 200
