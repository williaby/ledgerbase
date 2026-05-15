"""Comprehensive tests for ``ledgerbase/error_handlers.py``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from marshmallow import ValidationError
from werkzeug.exceptions import InternalServerError, NotFound

from ledgerbase.error_handlers import (
    _wants_json,
    handle_internal_error,
    handle_not_found,
    handle_validation_error,
    register_error_handlers,
)

if TYPE_CHECKING:
    from flask import Flask


def _register_test_routes(app: Flask) -> None:
    """Register routes that raise each error class we care about."""
    from flask import abort

    @app.route("/raise/validation")
    def _raise_validation() -> str:
        raise ValidationError({"field": ["bad value"]})

    @app.route("/raise/internal")
    def _raise_internal() -> str:
        raise InternalServerError("boom")

    @app.route("/raise/not-found")
    def _raise_not_found() -> str:
        abort(404)

    register_error_handlers(app)


def test_wants_json_returns_true_when_json_preferred(app: Flask) -> None:
    """_wants_json returns True when application/json is preferred."""
    with app.test_request_context("/", headers={"Accept": "application/json"}):
        assert _wants_json() is True


def test_wants_json_returns_false_when_html_preferred(app: Flask) -> None:
    """_wants_json returns False when text/html is preferred."""
    with app.test_request_context("/", headers={"Accept": "text/html"}):
        assert _wants_json() is False


def test_validation_handler_returns_json(app: Flask) -> None:
    """Validation errors return a 422 JSON body when JSON is preferred."""
    _register_test_routes(app)
    client = app.test_client()
    response = client.get("/raise/validation", headers={"Accept": "application/json"})
    assert response.status_code == 422
    payload = response.get_json()
    assert payload == {"errors": {"field": ["bad value"]}}


def test_validation_handler_returns_html(app: Flask, template_folder) -> None:  # noqa: ANN001
    """Validation errors render the 422.html template when HTML is preferred."""
    _register_test_routes(app)
    client = app.test_client()
    response = client.get("/raise/validation", headers={"Accept": "text/html"})
    assert response.status_code == 422
    assert b"422" in response.data or b"Invalid Input" in response.data


def test_not_found_handler_returns_json(app: Flask) -> None:
    """404 responses are JSON when JSON is preferred."""
    _register_test_routes(app)
    client = app.test_client()
    response = client.get("/raise/not-found", headers={"Accept": "application/json"})
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not found"}


def test_not_found_handler_returns_html(app: Flask, template_folder) -> None:  # noqa: ANN001
    """404 responses render the 404.html template when HTML is preferred."""
    _register_test_routes(app)
    client = app.test_client()
    response = client.get("/raise/not-found", headers={"Accept": "text/html"})
    assert response.status_code == 404
    assert b"404" in response.data or b"Not Found" in response.data


def test_internal_handler_returns_json(app: Flask) -> None:
    """500 errors return JSON when JSON is preferred."""
    _register_test_routes(app)
    app.config["PROPAGATE_EXCEPTIONS"] = False
    client = app.test_client()
    response = client.get("/raise/internal", headers={"Accept": "application/json"})
    assert response.status_code == 500
    assert response.get_json() == {"error": "Internal server error"}


def test_internal_handler_returns_html(app: Flask, template_folder) -> None:  # noqa: ANN001
    """500 errors render the 500.html template when HTML is preferred."""
    _register_test_routes(app)
    app.config["PROPAGATE_EXCEPTIONS"] = False
    client = app.test_client()
    response = client.get("/raise/internal", headers={"Accept": "text/html"})
    assert response.status_code == 500
    assert b"500" in response.data or b"Server Error" in response.data


def test_register_error_handlers_attaches_three_handlers(app: Flask) -> None:
    """register_error_handlers wires handlers that respond to each error class.

    Asserts via public behaviour (the Flask test client) rather than poking
    at the internal ``app.error_handler_spec`` table, which is not part of
    Flask's public API and shifts between releases.
    """
    _register_test_routes(app)
    app.config["PROPAGATE_EXCEPTIONS"] = False
    client = app.test_client()

    validation = client.get("/raise/validation", headers={"Accept": "application/json"})
    not_found = client.get("/raise/not-found", headers={"Accept": "application/json"})
    internal = client.get("/raise/internal", headers={"Accept": "application/json"})

    assert validation.status_code == 422
    assert not_found.status_code == 404
    assert internal.status_code == 500


def test_handle_validation_error_direct_call_json(app: Flask) -> None:
    """The handler can be invoked directly inside a request context."""
    err = ValidationError({"name": ["required"]})
    with app.test_request_context("/", headers={"Accept": "application/json"}):
        response, status = handle_validation_error(err)
        assert status == 422
        assert response.get_json() == {"errors": {"name": ["required"]}}


def test_handle_not_found_direct_call_json(app: Flask) -> None:
    """Direct call to handle_not_found returns the JSON payload."""
    with app.test_request_context("/", headers={"Accept": "application/json"}):
        response, status = handle_not_found(NotFound())
        assert status == 404
        assert response.get_json() == {"error": "Not found"}


def test_handle_internal_error_direct_call_json(app: Flask) -> None:
    """Direct call to handle_internal_error logs and returns JSON."""
    with app.test_request_context("/", headers={"Accept": "application/json"}):
        response, status = handle_internal_error(RuntimeError("kaboom"))
        assert status == 500
        assert response.get_json() == {"error": "Internal server error"}
