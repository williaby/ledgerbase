# Import Flask and Response for type hinting
from marshmallow import ValidationError

from flask import Flask, Response, jsonify, render_template, request

# Note: If using Python < 3.9, you might need: from typing import Tuple, Union
# And then use Union[Response, str] instead of Response | str
# And Tuple[Union[Response, str], int] instead of tuple[Response | str, int]


# Annotate the 'app' parameter
def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    # Annotate the 'error' parameter and the return type
    # (tuple of Response/str and status code)
    def handle_validation_error(error: ValidationError) -> tuple[Response | str, int]:
        # error.messages is typically Dict[str, List[str]] but can vary.
        # We don't need to hint it unless mypy complains further.
        if _wants_json():
            return jsonify({"errors": error.messages}), 422
        return render_template("422.html", errors=error.messages), 422

    @app.errorhandler(404)
    # Annotate 'error' (using generic Exception) and the return type
    def not_found(error: Exception) -> tuple[Response | str, int]:
        if _wants_json():
            return jsonify({"error": "Not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    # Annotate 'error' (using generic Exception) and the return type
    def internal_error(error: Exception) -> tuple[Response | str, int]:
        app.logger.exception(
            f"Unhandled exception occurred: {error}"
        )  # Log the actual error
        if _wants_json():
            return jsonify({"error": "Internal server error"}), 500
        # Ensure render_template returns a tuple with the status code for consistency
        return render_template("500.html"), 500


def _wants_json() -> bool:
    """Check if the client wants a JSON response based on Accept headers."""
    # Note: request proxy object doesn't require explicit type hinting here usually.
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    # Using direct comparison should be slightly clearer
    return best == "application/json"
