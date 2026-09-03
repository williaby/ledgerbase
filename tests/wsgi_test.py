"""Unit tests for the WSGI entry point."""

from flask import Flask


def test_wsgi_exposes_a_flask_app() -> None:
    """The wsgi module exposes a ready-to-serve Flask application."""
    from ledgerbase import wsgi

    assert isinstance(wsgi.app, Flask)


def test_wsgi_app_serves_the_index_route() -> None:
    """The WSGI application answers on the index route."""
    from ledgerbase import wsgi

    wsgi.app.config.update(TESTING=True)
    response = wsgi.app.test_client().get("/")
    assert b"LedgerBase API is running." in response.data
