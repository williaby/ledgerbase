"""Tests for the WSGI entry-point at ``ledgerbase/wsgi.py``."""

from __future__ import annotations

import importlib

import pytest


def _import_wsgi_with_safe_logging(
    monkeypatch: pytest.MonkeyPatch,
):
    """Import ``ledgerbase.wsgi`` with file-logging disabled.

    Importing the module constructs the Flask app at import time via
    ``create_app()``, which invokes ``configure_logging`` and would otherwise
    create ``src/logs/ledgerbase.log`` on disk. Patch the logging hook out
    before the module is (re)loaded so the test stays side-effect-free.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import ledgerbase

    monkeypatch.setattr(ledgerbase, "configure_logging", lambda _app: None)

    from ledgerbase import wsgi

    return importlib.reload(wsgi)


def test_wsgi_app_is_a_flask_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """Importing the wsgi module exposes a callable Flask app."""
    from flask import Flask

    wsgi = _import_wsgi_with_safe_logging(monkeypatch)
    assert isinstance(wsgi.app, Flask)


def test_wsgi_app_responds_to_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """The WSGI app's root route still serves the running message."""
    wsgi = _import_wsgi_with_safe_logging(monkeypatch)

    response = wsgi.app.test_client().get("/")
    assert response.status_code == 200
    assert b"LedgerBase API is running." in response.data
