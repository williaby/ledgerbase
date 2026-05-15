"""Shared pytest fixtures for the ledgerbase test suite."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from flask.testing import FlaskClient

    from flask import Flask


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Iterator[Flask]:
    """Build a Flask app using the factory with an in-memory SQLite DB."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.delenv("SENTRY_DSN", raising=False)

    # Prevent ``configure_logging`` from creating ``src/logs/ledgerbase.log``
    # during the test run -- the factory invokes it before TESTING=True is
    # set, so patch the name as it was re-exported into the package.
    import ledgerbase as _ledger_pkg

    monkeypatch.setattr(_ledger_pkg, "configure_logging", lambda _app: None)

    # Ensure ``ExampleModel`` is registered against the current ``db.metadata``
    # so ``db.create_all()`` actually creates its table.
    import ledgerbase.models  # noqa: F401
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
