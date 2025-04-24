##: name = error_handlers.py
##: description = Flask error handler registrations for ValidationError, 404, and 500
##: category = api
##: usage = from error_handlers import register_error_handlers
##:          register_error_handlers(app)
##: behavior = Registers error handlers on the Flask app for JSON or HTML responses
##: inputs = app: Flask
##: outputs = HTTP error responses (JSON or HTML)
##: dependencies = Flask, marshmallow
##: author = Byron Williams
##: last_modified = 2025-04-24
##: tags = error handling, api, flask
##: changelog =
#   - Parameter for 404 handler renamed to `_error: NotFound` to satisfy linting
#   - Removed `Any` import and ANN401 warnings fixed

"""Module defining and registering Flask error handlers.

Provides handlers for marshmallow ValidationError (422), 404 Not Found,
and 500 Internal Server Error, responding in JSON or rendered HTML
based on the client's Accept header.
"""


from marshmallow import ValidationError
from werkzeug.exceptions import InternalServerError, NotFound

from flask import Flask, Response, current_app, jsonify, render_template, request


def _wants_json() -> bool:
    """Check if the client prefers JSON responses."""
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "application/json"


def handle_validation_error(
    error: ValidationError,
) -> Response | str | tuple[Response | str, int]:
    """Handle marshmallow validation errors by returning JSON or HTML 422 responses.

    Args:
        error (ValidationError): The validation error instance.

    """
    if _wants_json():
        return jsonify({"errors": error.messages}), 422
    return render_template("422.html", errors=error.messages), 422


def handle_not_found(
    _error: NotFound,
) -> Response | str | tuple[Response | str, int]:
    """Handle 404 Not Found errors by returning JSON or HTML 404 responses.

    Args:
        _error (NotFound): The exception instance (unused).

    """
    if _wants_json():
        return jsonify({"error": "Not found"}), 404
    return render_template("404.html"), 404


def handle_internal_error(
    error: Exception,
) -> Response | str | tuple[Response | str, int]:
    """Handle unhandled exceptions by logging and returning JSON or HTML 500 responses.

    Args:
        error (Exception): The exception instance.

    """
    current_app.logger.exception("Unhandled exception occurred: %s", error)
    if _wants_json():
        return jsonify({"error": "Internal server error"}), 500
    return render_template("500.html"), 500


def register_error_handlers(app: Flask) -> None:
    """Register error handlers on the Flask application."""
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(NotFound, handle_not_found)
    app.register_error_handler(InternalServerError, handle_internal_error)
