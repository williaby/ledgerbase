"""Shared pytest fixtures for the ledgerbase test suite."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pytest

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Iterator[Flask]:
    """Build a Flask app using the factory with an in-memory SQLite DB."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.delenv("SENTRY_DSN", raising=False)

    from ledgerbase import create_app, db

    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    # The factory's template path resolution points at ``src/templates``;
    # tests need to render real templates from the project ``templates`` dir.
    flask_app.template_folder = str(TEMPLATES_DIR)
    flask_app.jinja_loader = __import__("jinja2").FileSystemLoader(str(TEMPLATES_DIR))

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Return a Flask test client bound to the test app."""
    return app.test_client()


@pytest.fixture
def template_folder(monkeypatch: pytest.MonkeyPatch) -> Path:
    """Provide the absolute path to the project templates folder."""
    monkeypatch.chdir(PROJECT_ROOT)
    return TEMPLATES_DIR
