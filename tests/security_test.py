"""Unit tests for the Flask security helpers."""

import logging
from pathlib import Path

import pytest

from flask import Flask
from ledgerbase import security

HTTP_OK = 200
HTTP_TOO_MANY_REQUESTS = 429
RATE_LIMIT_ATTEMPTS = 7

EXPECTED_HEADERS = {
    "Content-Security-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
}


def _bare_app() -> Flask:
    app = Flask(__name__)
    app.config.update(TESTING=True)
    return app


def test_apply_secure_headers_sets_all_headers() -> None:
    """Every response carries the full set of hardening headers."""
    app = _bare_app()
    security.apply_secure_headers(app)

    @app.route("/")
    def index() -> str:
        return "ok"

    response = app.test_client().get("/")
    assert response.status_code == HTTP_OK
    assert set(response.headers.keys()) >= EXPECTED_HEADERS
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_configure_rate_limiting_registers_login_route() -> None:
    """configure_rate_limiting adds a /login route to the app."""
    app = _bare_app()
    security.configure_rate_limiting(app)
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/login" in rules


def test_configure_rate_limiting_enforces_the_limit() -> None:
    """The /login route rejects traffic once its per-minute budget is spent."""
    app = _bare_app()
    security.configure_rate_limiting(app)
    client = app.test_client()
    statuses = [client.get("/login").status_code for _ in range(RATE_LIMIT_ATTEMPTS)]
    assert statuses[0] == HTTP_OK
    assert HTTP_TOO_MANY_REQUESTS in statuses


def test_configure_logging_skipped_when_testing() -> None:
    """No file handler is attached while the app is in testing mode."""
    app = _bare_app()
    before = len(app.logger.handlers)
    security.configure_logging(app)
    assert len(app.logger.handlers) == before


def test_configure_logging_skipped_when_debug() -> None:
    """No file handler is attached while the app is in debug mode."""
    app = Flask(__name__)
    app.debug = True
    before = len(app.logger.handlers)
    security.configure_logging(app)
    assert len(app.logger.handlers) == before


def test_configure_logging_attaches_rotating_file_handler(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A rotating file handler is attached for non-debug, non-testing apps."""
    app = Flask(__name__)
    app.debug = False
    app.config.update(TESTING=False)

    fake_module_file = tmp_path / "pkg" / "security.py"
    fake_module_file.parent.mkdir(parents=True)
    monkeypatch.setattr(security, "__file__", str(fake_module_file))

    security.configure_logging(app)

    handlers = [
        handler
        for handler in app.logger.handlers
        if isinstance(handler, security.RotatingFileHandler)
    ]
    assert handlers
    handler = handlers[0]
    assert handler.level == logging.INFO
    assert (tmp_path / "logs" / "ledgerbase.log").exists()
    handler.close()
    app.logger.removeHandler(handler)
