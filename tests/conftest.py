"""Shared pytest fixtures for the LedgerBase test suite."""

from pathlib import Path

import pytest

from flask import Flask
from ledgerbase.error_handlers import register_error_handlers

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "templates"


@pytest.fixture
def app() -> Flask:
    """Return a minimal Flask app wired to the repository template directory."""
    flask_app = Flask(__name__, template_folder=str(TEMPLATE_DIR))
    flask_app.config.update(TESTING=True)
    register_error_handlers(flask_app)

    @flask_app.route("/boom")
    def boom() -> str:
        raise RuntimeError

    return flask_app


@pytest.fixture
def client(app: Flask):  # noqa: ANN201
    """Return a test client for the minimal Flask app."""
    return app.test_client()
