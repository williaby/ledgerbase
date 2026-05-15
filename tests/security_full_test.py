"""Comprehensive tests for ``ledgerbase/security.py``."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from ledgerbase.security import (
    apply_secure_headers,
    configure_logging,
    configure_rate_limiting,
)

if TYPE_CHECKING:
    from flask import Flask


def _make_bare_flask_app() -> Flask:
    """Build a plain Flask app with no extensions attached."""
    from flask import Flask

    app = Flask(__name__)
    app.add_url_rule("/", "index", lambda: "ok")
    return app


def test_secure_headers_attached_to_response() -> None:
    """apply_secure_headers wires an after_request hook that sets every header."""
    app = _make_bare_flask_app()
    apply_secure_headers(app)

    client = app.test_client()
    response = client.get("/")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "geolocation=()" in response.headers["Permissions-Policy"]


def test_csp_header_contains_all_clauses() -> None:
    """The Content-Security-Policy header lists each expected directive."""
    app = _make_bare_flask_app()
    apply_secure_headers(app)
    client = app.test_client()
    csp = client.get("/").headers["Content-Security-Policy"]
    for fragment in (
        "default-src 'self'",
        "script-src 'self'",
        "img-src 'self' data:",
        "object-src 'none'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
    ):
        assert fragment in csp


def test_configure_rate_limiting_adds_login_route() -> None:
    """configure_rate_limiting attaches a /login endpoint."""
    app = _make_bare_flask_app()
    configure_rate_limiting(app)

    client = app.test_client()
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login attempt" in response.data


def test_rate_limiter_enforces_per_minute_cap() -> None:
    """After exceeding the rate cap, /login returns 429.

    Asserts both that an early request still succeeds (200) and that
    later requests get throttled (429), so the test doesn't pass when
    the limiter rejects from the very first call.
    """
    app = _make_bare_flask_app()
    configure_rate_limiting(app)
    client = app.test_client()

    statuses = [client.get("/login").status_code for _ in range(7)]
    assert statuses[0] == 200
    assert 429 in statuses


def test_configure_logging_skips_setup_in_debug_mode(tmp_path: Path) -> None:
    """When app.debug=True, no file handler is attached."""
    app = _make_bare_flask_app()
    app.debug = True
    before = list(app.logger.handlers)
    configure_logging(app)
    after = list(app.logger.handlers)
    assert before == after


def test_configure_logging_skips_setup_in_testing_mode() -> None:
    """When app.testing=True, no file handler is attached."""
    app = _make_bare_flask_app()
    app.testing = True
    before = list(app.logger.handlers)
    configure_logging(app)
    after = list(app.logger.handlers)
    assert before == after


def test_configure_logging_attaches_file_handler_in_production(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Non-debug, non-test apps get a RotatingFileHandler installed."""
    import ledgerbase.security as security_mod

    log_dir = tmp_path / "logs"

    class _FakeFileFactory:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.level = logging.NOTSET
            self.formatter: logging.Formatter | None = None
            log_dir.mkdir(parents=True, exist_ok=True)
            (log_dir / "ledgerbase.log").touch()

        def setLevel(self, level: int) -> None:
            self.level = level

        def setFormatter(self, fmt: logging.Formatter) -> None:
            self.formatter = fmt

        def handle(self, record: logging.LogRecord) -> None:
            return None

        @property
        def lock(self) -> None:
            return None

    monkeypatch.setattr(security_mod, "RotatingFileHandler", _FakeFileFactory)

    real_resolve = Path.resolve

    def _fake_resolve(self: Path, *args: object, **kwargs: object) -> Path:
        if "security.py" in str(self):
            return tmp_path / "src" / "ledgerbase" / "security.py"
        return real_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", _fake_resolve)

    app = _make_bare_flask_app()
    app.debug = False
    app.testing = False
    handlers_before = len(app.logger.handlers)
    configure_logging(app)
    handlers_after = len(app.logger.handlers)
    assert handlers_after == handlers_before + 1
