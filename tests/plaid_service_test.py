"""Tests for the Plaid HTTP wrapper in ``services/plaid_service.py``.

The Plaid client is a thin wrapper over ``requests``; the tests mock the
``requests.post`` call so they exercise every branch without hitting the
network. Scenarios covered:

* Successful sync / fetch
* Empty result payload
* API error (non-2xx HTTP status -> ``raise_for_status``)
* Token expiry / connection error (``requests.RequestException``)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from services import plaid_service
from services.plaid_service import (
    PLAID_BASE_URLS,
    create_link_token,
    get_accounts,
    get_transactions,
    plaid_request,
    sync_transactions,
)


def _make_response(
    payload: dict[str, Any] | None = None,
    status_code: int = 200,
) -> MagicMock:
    """Build a fake ``requests.Response`` for use with ``requests.post`` mocks."""
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.text = "" if payload is None else str(payload)
    response.json.return_value = payload if payload is not None else {}
    if status_code >= 400:
        http_err = requests.HTTPError(f"{status_code} error", response=response)
        response.raise_for_status.side_effect = http_err
    else:
        response.raise_for_status.return_value = None
    return response


def test_plaid_base_urls_known_environments() -> None:
    """The base URL map covers the three Plaid environments."""
    assert PLAID_BASE_URLS["sandbox"] == "https://sandbox.plaid.com"
    assert PLAID_BASE_URLS["development"] == "https://development.plaid.com"
    assert PLAID_BASE_URLS["production"] == "https://production.plaid.com"


def test_plaid_request_successful_call_returns_json() -> None:
    """A 200 response with JSON body is returned unchanged."""
    payload = {"accounts": [{"account_id": "abc"}]}
    with patch.object(plaid_service.requests, "post") as mock_post:
        mock_post.return_value = _make_response(payload)
        result = plaid_request("/accounts/get", {"access_token": "tok"})
    assert result == payload
    mock_post.assert_called_once()


def test_plaid_request_injects_client_id_and_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """plaid_request must always inject client_id and secret into the payload."""
    monkeypatch.setattr(plaid_service, "PLAID_CLIENT_ID", "id-123")
    monkeypatch.setattr(plaid_service, "PLAID_SECRET", "secret-456")
    captured: dict[str, Any] = {}

    def _fake_post(url: str, **kwargs: Any) -> MagicMock:
        captured["url"] = url
        captured["payload"] = kwargs["json"]
        return _make_response({"ok": True})

    with patch.object(plaid_service.requests, "post", side_effect=_fake_post):
        result = plaid_request("/endpoint", {"foo": "bar"})

    assert result == {"ok": True}
    assert captured["payload"]["client_id"] == "id-123"
    assert captured["payload"]["secret"] == "secret-456"
    assert captured["payload"]["foo"] == "bar"


def test_plaid_request_returns_none_on_request_exception(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Network / connection failures should produce a None return value."""
    with patch.object(
        plaid_service.requests,
        "post",
        side_effect=requests.ConnectionError("network down"),
    ):
        result = plaid_request("/endpoint", {})
    assert result is None
    out = capsys.readouterr().out
    assert "Plaid API request failed" in out


def test_plaid_request_returns_none_on_http_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An HTTP error (e.g. token expiry 401) returns None and prints diagnostics."""
    bad_response = _make_response(
        {"error_code": "INVALID_ACCESS_TOKEN"},
        status_code=401,
    )
    with patch.object(plaid_service.requests, "post", return_value=bad_response):
        result = plaid_request("/endpoint", {"access_token": "expired"})
    assert result is None
    out = capsys.readouterr().out
    assert "Plaid API request failed" in out
    assert "Response:" in out


def test_create_link_token_uses_correct_endpoint_and_payload() -> None:
    """create_link_token posts to /link/token/create with the user payload."""
    with patch.object(plaid_service, "plaid_request") as mock_request:
        mock_request.return_value = {"link_token": "lt-1"}
        result = create_link_token("user-42")

    assert result == {"link_token": "lt-1"}
    endpoint, payload = mock_request.call_args.args
    assert endpoint == "/link/token/create"
    assert payload["user"] == {"client_user_id": "user-42"}
    assert payload["products"] == ["transactions"]
    assert payload["country_codes"] == ["US"]
    assert payload["language"] == "en"
    assert payload["client_name"] == "LedgerBase"


def test_create_link_token_uses_default_user_id() -> None:
    """create_link_token has a stable default for the user_id parameter."""
    with patch.object(plaid_service, "plaid_request") as mock_request:
        mock_request.return_value = {"link_token": "default"}
        create_link_token()
    _, payload = mock_request.call_args.args
    assert payload["user"]["client_user_id"] == "user-unique-id"


def test_get_accounts_calls_correct_endpoint() -> None:
    """get_accounts posts the access token to /accounts/get."""
    with patch.object(plaid_service, "plaid_request") as mock_request:
        mock_request.return_value = {"accounts": []}
        result = get_accounts("tok-1")
    assert result == {"accounts": []}
    endpoint, payload = mock_request.call_args.args
    assert endpoint == "/accounts/get"
    assert payload == {"access_token": "tok-1"}


def test_get_transactions_without_options() -> None:
    """get_transactions omits the options key when none are supplied."""
    with patch.object(plaid_service, "plaid_request") as mock_request:
        mock_request.return_value = {"transactions": []}
        result = get_transactions("tok", "2024-01-01", "2024-01-31")

    assert result == {"transactions": []}
    endpoint, payload = mock_request.call_args.args
    assert endpoint == "/transactions/get"
    assert payload == {
        "access_token": "tok",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    }
    assert "options" not in payload


def test_get_transactions_with_options() -> None:
    """When options are supplied they are forwarded to the Plaid call."""
    with patch.object(plaid_service, "plaid_request") as mock_request:
        mock_request.return_value = {"transactions": [{"id": "t1"}]}
        result = get_transactions(
            "tok",
            "2024-01-01",
            "2024-01-31",
            options={"count": 100, "offset": 0},
        )

    assert result == {"transactions": [{"id": "t1"}]}
    _, payload = mock_request.call_args.args
    assert payload["options"] == {"count": 100, "offset": 0}


def test_get_transactions_empty_result() -> None:
    """An empty transactions list passes through unchanged."""
    with patch.object(plaid_service, "plaid_request") as mock_request:
        mock_request.return_value = {"transactions": [], "total_transactions": 0}
        result = get_transactions("tok", "2024-01-01", "2024-01-31")
    assert result == {"transactions": [], "total_transactions": 0}


def test_get_transactions_api_error_returns_none() -> None:
    """When the underlying plaid_request returns None, get_transactions does too."""
    with patch.object(plaid_service, "plaid_request", return_value=None):
        result = get_transactions("tok", "2024-01-01", "2024-01-31")
    assert result is None


def test_sync_transactions_without_cursor() -> None:
    """sync_transactions omits the cursor key when none is given."""
    with patch.object(plaid_service, "plaid_request") as mock_request:
        mock_request.return_value = {"added": [], "modified": [], "removed": []}
        result = sync_transactions("tok-2")

    assert result == {"added": [], "modified": [], "removed": []}
    endpoint, payload = mock_request.call_args.args
    assert endpoint == "/transactions/sync"
    assert payload == {"access_token": "tok-2"}
    assert "cursor" not in payload


def test_sync_transactions_with_cursor() -> None:
    """sync_transactions forwards the cursor when present."""
    with patch.object(plaid_service, "plaid_request") as mock_request:
        mock_request.return_value = {"added": [], "next_cursor": "next"}
        sync_transactions("tok-2", cursor="prev-cursor")
    _, payload = mock_request.call_args.args
    assert payload["cursor"] == "prev-cursor"


def test_sync_transactions_token_expiry_returns_none(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """If the access token is invalid, sync returns None (the HTTP error path)."""
    bad = _make_response({"error_code": "ITEM_LOGIN_REQUIRED"}, status_code=400)
    with patch.object(plaid_service.requests, "post", return_value=bad):
        result = sync_transactions("expired-tok")
    assert result is None
    out = capsys.readouterr().out
    assert "Plaid API request failed" in out


def test_sync_transactions_empty_result() -> None:
    """An empty sync (no changes) round-trips through the function."""
    empty_payload = {
        "added": [],
        "modified": [],
        "removed": [],
        "next_cursor": "",
        "has_more": False,
    }
    with patch.object(plaid_service, "plaid_request", return_value=empty_payload):
        result = sync_transactions("tok")
    assert result == empty_payload
    assert result["has_more"] is False
    assert result["added"] == []
