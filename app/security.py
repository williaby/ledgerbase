import logging
import os
from logging.handlers import RotatingFileHandler

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask import Flask, Response

# Import Flask and Response for type hinting


# Annotate 'app' parameter and specify no return value (None)
def apply_secure_headers(app: Flask) -> None:
    @app.after_request
    # Annotate 'response' parameter and its return type
    def set_secure_headers(response: Response) -> Response:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "font-src 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self';"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), camera=(), microphone=()"
        )
        return response


# Annotate 'app' parameter and specify no return value (None)
def configure_rate_limiting(app: Flask) -> None:
    # Note: Limiter type hinting can be complex, often omitted unless needed
    limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

    @app.route("/login")
    @limiter.limit("5 per minute")
    # Annotate return type for the view function
    def login() -> str:
        # This view function returns a string
        return "Login attempt"


# Annotate 'app' parameter and specify no return value (None)
def configure_logging(app: Flask) -> None:
    # The original error might have pointed near here, but the annotation belongs
    # on the function definition line above.
    if not app.debug and not app.testing:
        logs_path = os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(logs_path, exist_ok=True)
        log_file = os.path.join(logs_path, "ledgerbase.log")
        # Note: Type hinting for handlers/formatters can be added for more
        # strictness but is often omitted for brevity.
        file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: " "%(message)s " "[in %(pathname)s:%(lineno)d]"
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("LedgerBase startup")
