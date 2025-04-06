from flask import jsonify, render_template, request
from marshmallow import ValidationError

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        if _wants_json():
            return jsonify({"errors": error.messages}), 422
        return render_template("422.html", errors=error.messages), 422

    @app.errorhandler(404)
    def not_found(error):
        if _wants_json():
            return jsonify({"error": "Not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Unhandled exception occurred")
        if _wants_json():
            return jsonify({"error": "Internal server error"}), 500
        return render_template("500.html"), 500

def _wants_json():
    return request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html
