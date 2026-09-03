"""Unit tests for the LedgerBase application factory."""

from pathlib import Path

import pytest

import ledgerbase

HTTP_OK = 200


def test_create_app_returns_configured_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """create_app returns a Flask app wired to the configured database URI."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///unit-test.db")
    app = ledgerbase.create_app()
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///unit-test.db"
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False


def test_create_app_defaults_the_database_uri(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create_app falls back to a local SQLite database when DATABASE_URL is unset."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    app = ledgerbase.create_app()
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///default.db"


def test_create_app_rejects_empty_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty DATABASE_URL is rejected rather than silently accepted."""
    monkeypatch.setenv("DATABASE_URL", "")
    with pytest.raises(ValueError, match="DATABASE_URL"):
        ledgerbase.create_app()


def test_create_app_uses_template_dir_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The sibling templates directory is used as the Jinja search path."""
    monkeypatch.setattr(Path, "is_dir", lambda _self: True)
    app = ledgerbase.create_app()
    assert app.template_folder is not None
    assert app.template_folder.endswith("templates")


def test_create_app_registers_core_routes() -> None:
    """create_app wires the index, login, and debug-sentry routes."""
    app = ledgerbase.create_app()
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert {"/", "/login", "/debug-sentry"} <= rules


def test_index_route_responds() -> None:
    """The index route reports that the API is running."""
    app = ledgerbase.create_app()
    app.config.update(TESTING=True)
    response = app.test_client().get("/")
    assert response.status_code == HTTP_OK
    assert b"LedgerBase API is running." in response.data


def test_debug_sentry_route_raises() -> None:
    """The debug-sentry route deliberately raises a division error."""
    app = ledgerbase.create_app()
    app.config.update(TESTING=True)
    with pytest.raises(ZeroDivisionError):
        app.test_client().get("/debug-sentry")
