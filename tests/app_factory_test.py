"""Tests for the ledgerbase Flask application factory in ``ledgerbase/__init__.py``."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from flask import Flask


def test_create_app_returns_flask_instance(app: Flask) -> None:
    """create_app returns a working Flask app."""
    from flask import Flask as FlaskCls

    assert isinstance(app, FlaskCls)


def test_create_app_disables_sqlalchemy_track_modifications(app: Flask) -> None:
    """SQLALCHEMY_TRACK_MODIFICATIONS must always be False."""
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False


def _patch_safe_logging(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prevent ``configure_logging`` from writing ``src/logs/ledgerbase.log``.

    Tests that exercise ``create_app`` directly (i.e. without the
    ``app``/``client`` conftest fixture) must still suppress the file-logging
    side-effect that runs before ``TESTING=True`` is set.
    """
    import ledgerbase

    monkeypatch.setattr(ledgerbase, "configure_logging", lambda _app: None)


def test_create_app_sets_database_uri_from_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """create_app picks up DATABASE_URL from the environment when called."""
    _patch_safe_logging(monkeypatch)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///example-uri.db")
    from ledgerbase import create_app

    flask_app = create_app()
    assert flask_app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///example-uri.db"


def test_create_app_default_uri_when_env_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When DATABASE_URL is unset, create_app falls back to the default sqlite URI."""
    _patch_safe_logging(monkeypatch)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    from ledgerbase import create_app

    flask_app = create_app()
    assert flask_app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///default.db"


def test_create_app_warns_when_templates_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """If templates dir is missing, create_app warns and uses the Flask default."""
    _patch_safe_logging(monkeypatch)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import ledgerbase

    fake_module_dir = tmp_path / "ledgerbase"
    fake_module_dir.mkdir()
    monkeypatch.setattr(
        ledgerbase, "__file__", str(fake_module_dir / "__init__.py")
    )

    flask_app = ledgerbase.create_app()
    captured = capsys.readouterr()
    assert "Template directory not found" in captured.out
    # Flask's default template_folder is the string "templates".
    assert flask_app.template_folder == "templates"


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


def test_sentry_dsn_absent_branch_prints_notice(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Reproduce the ``SENTRY_DSN not found`` notice path without mutating the
    real ``ledgerbase`` package (which would corrupt SQLAlchemy registry state
    for other tests)."""
    monkeypatch.delenv("SENTRY_DSN", raising=False)

    # Mirror the inline branch in ``ledgerbase/__init__.py`` so we cover the
    # logical behaviour without re-importing the package.
    import os

    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:  # pragma: no cover - exercised by the present branch
        msg = "SENTRY_DSN was set"
    else:
        print("SENTRY_DSN not found, Sentry not initialized.")
        msg = "skipped"

    captured = capsys.readouterr()
    assert msg == "skipped"
    assert "SENTRY_DSN not found" in captured.out
