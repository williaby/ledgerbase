"""Unit tests for the Plaid API service wrapper."""

from typing import Any

import pytest
import requests

from services import plaid_service


class _FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, payload: dict[str, Any], *, fail: bool = False) -> None:
        self._payload = payload
        self._fail = fail
        self.text = "response body"

    def raise_for_status(self) -> None:
        if self._fail:
            msg = "boom"
            raise requests.HTTPError(msg)

    def json(self) -> dict[str, Any]:
        return self._payload


@pytest.fixture
def captured(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Capture the outbound request and return a canned success payload."""
    recorded: dict[str, Any] = {}

    def fake_post(
        url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],
        timeout: float,
    ) -> _FakeResponse:
        recorded["url"] = url
        recorded["json"] = json
        recorded["headers"] = headers
        recorded["timeout"] = timeout
        return _FakeResponse({"ok": True})

    monkeypatch.setattr(plaid_service.requests, "post", fake_post)
    return recorded


def test_base_urls_cover_every_environment() -> None:
    """Every supported Plaid environment maps to an HTTPS base URL."""
    assert set(plaid_service.PLAID_BASE_URLS) == {
        "sandbox",
        "development",
        "production",
    }
    assert all(
        url.startswith("https://") for url in plaid_service.PLAID_BASE_URLS.values()
    )


def test_plaid_request_success(captured: dict[str, Any]) -> None:
    """A successful call returns the decoded JSON body."""
    result = plaid_service.plaid_request("/any", {"key": "value"})
    assert result == {"ok": True}
    assert captured["url"].endswith("/any")
    assert captured["timeout"] == plaid_service.DEFAULT_TIMEOUT
    assert captured["headers"] == plaid_service.HEADERS


def test_plaid_request_injects_credentials(captured: dict[str, Any]) -> None:
    """The client id and secret are merged into every payload."""
    plaid_service.plaid_request("/any", {"key": "value"})
    assert captured["json"]["key"] == "value"
    assert "client_id" in captured["json"]
    assert "secret" in captured["json"]


def test_plaid_request_returns_none_on_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A non-2xx response is swallowed and reported as None."""

    def fake_post(
        _url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],
        timeout: float,
    ) -> _FakeResponse:
        del json, headers, timeout
        return _FakeResponse({}, fail=True)

    monkeypatch.setattr(plaid_service.requests, "post", fake_post)
    assert plaid_service.plaid_request("/any", {}) is None


def test_plaid_request_returns_none_on_connection_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A transport failure before any response is also reported as None."""

    def fake_post(
        _url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],
        timeout: float,
    ) -> _FakeResponse:
        del json, headers, timeout
        msg = "unreachable"
        raise requests.ConnectionError(msg)

    monkeypatch.setattr(plaid_service.requests, "post", fake_post)
    assert plaid_service.plaid_request("/any", {}) is None


def test_create_link_token(captured: dict[str, Any]) -> None:
    """create_link_token posts the documented link-token payload."""
    assert plaid_service.create_link_token("user-42") == {"ok": True}
    assert captured["url"].endswith("/link/token/create")
    assert captured["json"]["user"] == {"client_user_id": "user-42"}
    assert captured["json"]["products"] == ["transactions"]


def test_get_accounts(captured: dict[str, Any]) -> None:
    """get_accounts posts the access token to the accounts endpoint."""
    assert plaid_service.get_accounts("tok") == {"ok": True}
    assert captured["url"].endswith("/accounts/get")
    assert captured["json"]["access_token"] == "tok"


def test_get_transactions_without_options(captured: dict[str, Any]) -> None:
    """get_transactions omits the options key when none are supplied."""
    plaid_service.get_transactions("tok", "2026-01-01", "2026-01-31")
    assert captured["url"].endswith("/transactions/get")
    assert captured["json"]["start_date"] == "2026-01-01"
    assert captured["json"]["end_date"] == "2026-01-31"
    assert "options" not in captured["json"]


def test_get_transactions_with_options(captured: dict[str, Any]) -> None:
    """get_transactions forwards caller-supplied options."""
    plaid_service.get_transactions(
        "tok",
        "2026-01-01",
        "2026-01-31",
        options={"count": 10},
    )
    assert captured["json"]["options"] == {"count": 10}


def test_sync_transactions_without_cursor(captured: dict[str, Any]) -> None:
    """sync_transactions omits the cursor on a first-page request."""
    plaid_service.sync_transactions("tok")
    assert captured["url"].endswith("/transactions/sync")
    assert "cursor" not in captured["json"]


def test_sync_transactions_with_cursor(captured: dict[str, Any]) -> None:
    """sync_transactions forwards the cursor for incremental syncs."""
    plaid_service.sync_transactions("tok", cursor="abc")
    assert captured["json"]["cursor"] == "abc"
