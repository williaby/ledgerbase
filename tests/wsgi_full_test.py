"""Tests for the WSGI entry-point at ``ledgerbase/wsgi.py``."""

from __future__ import annotations

import importlib

import pytest


def test_wsgi_app_is_a_flask_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """Importing the wsgi module exposes a callable Flask app."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    from flask import Flask

    import ledgerbase

    importlib.reload(ledgerbase)
    from ledgerbase import wsgi

    importlib.reload(wsgi)

    assert isinstance(wsgi.app, Flask)


def test_wsgi_app_responds_to_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """The WSGI app's root route still serves the running message."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import ledgerbase

    importlib.reload(ledgerbase)
    from ledgerbase import wsgi

    importlib.reload(wsgi)

    response = wsgi.app.test_client().get("/")
    assert response.status_code == 200
    assert b"LedgerBase API is running." in response.data
