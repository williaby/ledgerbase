"""Unit tests for the Flask error handlers."""

from marshmallow import ValidationError
from werkzeug.exceptions import InternalServerError, NotFound

from flask import Flask
from ledgerbase import error_handlers

JSON_HEADERS = {"Accept": "application/json"}
HTML_HEADERS = {"Accept": "text/html"}

HTTP_NOT_FOUND = 404
HTTP_UNPROCESSABLE = 422
HTTP_SERVER_ERROR = 500


def test_wants_json_true(app: Flask) -> None:
    """_wants_json is True when the client prefers JSON."""
    with app.test_request_context("/", headers=JSON_HEADERS):
        assert error_handlers._wants_json() is True  # noqa: SLF001


def test_wants_json_false(app: Flask) -> None:
    """_wants_json is False when the client prefers HTML."""
    with app.test_request_context("/", headers=HTML_HEADERS):
        assert error_handlers._wants_json() is False  # noqa: SLF001


def test_validation_error_json(app: Flask) -> None:
    """A ValidationError renders a 422 JSON body when JSON is preferred."""
    with app.test_request_context("/", headers=JSON_HEADERS):
        response, status = error_handlers.handle_validation_error(
            ValidationError({"field": ["bad"]}),
        )
    assert status == HTTP_UNPROCESSABLE
    assert response.get_json() == {"errors": {"field": ["bad"]}}


def test_validation_error_html(app: Flask) -> None:
    """A ValidationError renders the 422 template when HTML is preferred."""
    with app.test_request_context("/", headers=HTML_HEADERS):
        body, status = error_handlers.handle_validation_error(
            ValidationError({"field": ["bad"]}),
        )
    assert status == HTTP_UNPROCESSABLE
    assert isinstance(body, str)


def test_not_found_json(app: Flask) -> None:
    """A 404 renders a JSON body when JSON is preferred."""
    with app.test_request_context("/", headers=JSON_HEADERS):
        response, status = error_handlers.handle_not_found(NotFound())
    assert status == HTTP_NOT_FOUND
    assert response.get_json() == {"error": "Not found"}


def test_not_found_html(app: Flask) -> None:
    """A 404 renders the 404 template when HTML is preferred."""
    with app.test_request_context("/", headers=HTML_HEADERS):
        body, status = error_handlers.handle_not_found(NotFound())
    assert status == HTTP_NOT_FOUND
    assert isinstance(body, str)


def test_internal_error_json(app: Flask) -> None:
    """A 500 renders a JSON body and logs the exception."""
    with app.test_request_context("/", headers=JSON_HEADERS):
        response, status = error_handlers.handle_internal_error(
            InternalServerError(),
        )
    assert status == HTTP_SERVER_ERROR
    assert response.get_json() == {"error": "Internal server error"}


def test_internal_error_html(app: Flask) -> None:
    """A 500 renders the 500 template when HTML is preferred."""
    with app.test_request_context("/", headers=HTML_HEADERS):
        body, status = error_handlers.handle_internal_error(
            InternalServerError(),
        )
    assert status == HTTP_SERVER_ERROR
    assert isinstance(body, str)


def test_register_error_handlers_binds_all_three() -> None:
    """register_error_handlers registers a handler for each supported error."""
    flask_app = Flask(__name__)
    error_handlers.register_error_handlers(flask_app)
    by_code = flask_app.error_handler_spec[None]
    # Flask keys HTTPException handlers by status code and other
    # exception types by class.
    assert ValidationError in by_code[None]
    assert NotFound in by_code[HTTP_NOT_FOUND]
    assert InternalServerError in by_code[HTTP_SERVER_ERROR]
