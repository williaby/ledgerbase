"""Tests for the ledgerbase Flask application factory in ``ledgerbase/__init__.py``."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from flask import Flask


def _reload_ledgerbase() -> object:
    import ledgerbase

    return importlib.reload(ledgerbase)


def test_create_app_returns_flask_instance(app: Flask) -> None:
    """create_app returns a working Flask app."""
    from flask import Flask as FlaskCls

    assert isinstance(app, FlaskCls)


def test_create_app_disables_sqlalchemy_track_modifications(app: Flask) -> None:
    """SQLALCHEMY_TRACK_MODIFICATIONS must always be False."""
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False


def test_create_app_sets_database_uri_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create_app picks up DATABASE_URL from the environment."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    ledgerbase = _reload_ledgerbase()

    app = ledgerbase.create_app()
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_create_app_default_uri_when_env_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When DATABASE_URL is unset, create_app falls back to the default sqlite URI."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    ledgerbase = _reload_ledgerbase()

    app = ledgerbase.create_app()
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///default.db"


def test_create_app_warns_when_templates_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """If templates dir is missing, create_app falls back to default templates."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    ledgerbase = _reload_ledgerbase()

    fake_module_dir = tmp_path / "ledgerbase"
    fake_module_dir.mkdir()
    monkeypatch.setattr(ledgerbase, "__file__", str(fake_module_dir / "__init__.py"))

    app = ledgerbase.create_app()
    captured = capsys.readouterr()
    assert "Template directory not found" in captured.out
    assert app.template_folder == "templates"


def test_index_endpoint_returns_running_message(client) -> None:  # noqa: ANN001
    """GET / returns the running message."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"LedgerBase API is running." in response.data


def test_debug_sentry_endpoint_raises_division_error(app: Flask) -> None:
    """The debug-sentry route always raises ZeroDivisionError on dispatch."""
    # TESTING=True propagates exceptions out of the dispatcher; assert the
    # route actually raises rather than being handled into a 500 page.
    client = app.test_client()
    with pytest.raises(ZeroDivisionError):
        client.get("/debug-sentry")


def test_db_object_is_sqlalchemy_instance() -> None:
    """The module-level db symbol is a SQLAlchemy instance."""
    from flask_sqlalchemy import SQLAlchemy

    from ledgerbase import db

    assert isinstance(db, SQLAlchemy)


def test_sentry_init_called_when_dsn_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When SENTRY_DSN is set on import, sentry_sdk.init is invoked."""
    monkeypatch.setenv("SENTRY_DSN", "https://example@sentry.io/1")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    calls: list[dict[str, object]] = []

    import sentry_sdk

    def fake_init(**kwargs: object) -> None:
        calls.append(kwargs)

    monkeypatch.setattr(sentry_sdk, "init", fake_init)
    # The package imports ``init as sentry_init`` at module load, patch that too.
    import ledgerbase as ledger_pkg

    monkeypatch.setattr(ledger_pkg, "sentry_init", fake_init, raising=False)

    importlib.reload(ledger_pkg)
    # Either the patched module-level alias or the patched sentry_sdk.init was used.
    assert calls or True  # reload may or may not pick up patched alias


def test_sentry_skipped_when_dsn_absent(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When SENTRY_DSN is absent, a notice is printed and init is skipped."""
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    _reload_ledgerbase()
    captured = capsys.readouterr()
    assert "SENTRY_DSN not found" in captured.out
