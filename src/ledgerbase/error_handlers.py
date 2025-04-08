from marshmallow import ValidationError

from flask import Flask, Response, jsonify, render_template, request


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError) -> tuple[Response | str, int]:
        if _wants_json():
            return jsonify({"errors": error.messages}), 422
        return render_template("422.html", errors=error.messages), 422

    @app.errorhandler(404)
    def not_found(error: Exception) -> tuple[Response | str, int]:
        if _wants_json():
            return jsonify({"error": "Not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error: Exception) -> tuple[Response | str, int]:
        app.logger.exception(f"Unhandled exception occurred: {error}")
        if _wants_json():
            return jsonify({"error": "Internal server error"}), 500
        return render_template("500.html"), 500


def _wants_json() -> bool:
    """Check if the client prefers JSON responses."""
    best = request.accept_mimetypes.best_match(["application/json", "text/html"])
    return best == "application/json"
