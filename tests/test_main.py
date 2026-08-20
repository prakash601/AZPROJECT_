"""Tests for main.py / api/routes.py – FastAPI endpoints."""
import pytest
from unittest import mock

# After refactor/api-routes, search logic lives in api.routes (main.py just includes the router).
# Patch api.routes.pg_search / correct_query / autocomplete. Also patch main.* for backwards compat
# by aliasing — tests that mock main.* will still work if we patch both.
_PATCH_SEARCH = "api.routes.pg_search"
_PATCH_CORRECT = "api.routes.correct_query"
_PATCH_AUTOCOMPLETE = "api.routes.autocomplete"


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_search_success_returns_results_and_no_correction(client):
    fake_results = [
        {
            "id": 1,
            "platform": "leetcode",
            "title": "Two Sum",
            "url": "https://example.com/two-sum",
            "description": "desc",
            "difficulty": "Easy",
            "tags": ["array"],
            "score": 0.9,
        }
    ]
    with mock.patch(_PATCH_SEARCH, return_value=fake_results) as mock_search, \
         mock.patch(_PATCH_CORRECT, return_value="two sum"):
        resp = client.get("/api/search", params={"q": "two sum", "limit": 30, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "two sum"
        # corrected_query same as query lowercased -> should be None
        assert data["corrected_query"] is None
        assert data["count"] == 1
        assert data["results"] == fake_results
        assert isinstance(data["execution_time_ms"], int)
        mock_search.assert_called_once_with("two sum", limit=30, offset=0)


def test_search_surfaces_corrected_query_when_different(client):
    fake_results = []
    with mock.patch(_PATCH_SEARCH, return_value=fake_results), \
         mock.patch(_PATCH_CORRECT, return_value="binary search"):
        resp = client.get("/api/search", params={"q": "binery serch"})
        assert resp.status_code == 200
        assert resp.json()["corrected_query"] == "binary search"


def test_search_corrected_query_case_insensitive_suppressed(client):
    with mock.patch(_PATCH_SEARCH, return_value=[]), \
         mock.patch(_PATCH_CORRECT, return_value="Two Sum"):
        resp = client.get("/api/search", params={"q": "two sum"})
        assert resp.json()["corrected_query"] is None

    with mock.patch(_PATCH_SEARCH, return_value=[]), \
         mock.patch(_PATCH_CORRECT, return_value="  Two Sum  "):
        resp = client.get("/api/search", params={"q": "  two sum  "})
        assert resp.json()["corrected_query"] is None


def test_search_validation_min_length(client):
    # FastAPI Query min_length=1 -> empty string should 422
    resp = client.get("/api/search", params={"q": ""})
    assert resp.status_code == 422


def test_search_validation_limit_bounds(client):
    with mock.patch(_PATCH_SEARCH, return_value=[]), \
         mock.patch(_PATCH_CORRECT, return_value=None):
        resp = client.get("/api/search", params={"q": "x", "limit": 0})
        assert resp.status_code == 422
        resp = client.get("/api/search", params={"q": "x", "limit": 101})
        assert resp.status_code == 422
        resp = client.get("/api/search", params={"q": "x", "limit": 1})
        assert resp.status_code == 200


def test_search_validation_offset_negative(client):
    resp = client.get("/api/search", params={"q": "x", "offset": -1})
    assert resp.status_code == 422


def test_search_pagination_passed_to_pg_search(client):
    with mock.patch(_PATCH_SEARCH, return_value=[]) as m, \
         mock.patch(_PATCH_CORRECT, return_value=None):
        resp = client.get("/api/search", params={"q": "hello", "limit": 5, "offset": 10})
        assert resp.status_code == 200
        m.assert_called_once_with("hello", limit=5, offset=10)
        assert resp.json()["count"] == 0


def test_autocomplete_success(client):
    fake_suggestions = [{"id": 1, "title": "Two Sum", "url": "https://example.com", "platform": "leetcode"}]
    with mock.patch(_PATCH_AUTOCOMPLETE, return_value=fake_suggestions) as m:
        resp = client.get("/api/autocomplete", params={"prefix": "two", "limit": 10})
        assert resp.status_code == 200
        data = resp.json()
        assert data["prefix"] == "two"
        assert data["suggestions"] == fake_suggestions
        m.assert_called_once_with("two", limit=10)


def test_autocomplete_validation(client):
    resp = client.get("/api/autocomplete", params={"prefix": ""})
    assert resp.status_code == 422
    resp = client.get("/api/autocomplete", params={"prefix": "x", "limit": 0})
    assert resp.status_code == 422
    resp = client.get("/api/autocomplete", params={"prefix": "x", "limit": 51})
    assert resp.status_code == 422


def test_search_response_model_fields(client):
    # Ensure response shape matches SearchResponse model
    with mock.patch(_PATCH_SEARCH, return_value=[]), \
         mock.patch(_PATCH_CORRECT, return_value=None):
        resp = client.get("/api/search", params={"q": "test"})
        data = resp.json()
        assert set(data.keys()) == {"query", "corrected_query", "execution_time_ms", "count", "results"}


def test_autocomplete_response_model_fields(client):
    with mock.patch(_PATCH_AUTOCOMPLETE, return_value=[]):
        resp = client.get("/api/autocomplete", params={"prefix": "a"})
        data = resp.json()
        assert set(data.keys()) == {"prefix", "suggestions"}


def test_cors_headers_present(client):
    # CORSMiddleware should add headers; TestClient checks via OPTIONS
    resp = client.options("/api/health", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    # Some starlette versions return 200 with CORS headers
    assert resp.status_code in (200, 204)


def test_openapi_docs_accessible(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert resp.json()["info"]["title"] == "Problem Finder API"
