##: name = security.py
##: description = Flask security utilities for HTTP headers, rate limiting, and logging
##: category = security
##: usage = Import and use in Flask applications
##: behavior = Enhances Flask app security with headers, rate limiting, and logging
##: inputs = Flask application instance
##: outputs = Secured Flask application with headers, rate limiting, and logging
##: dependencies = Flask, flask_limiter
##: author = LedgerBase Team
##: last_modified = 2023-11-15
##: changelog = Initial version

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask import Flask, Response

"""Flask security utilities for enhancing application security.

This module provides functions to add security headers to HTTP responses,
configure rate limiting for routes, and set up logging for Flask applications.
"""


def apply_secure_headers(app: Flask) -> None:
    """Apply secure headers to all responses in the Flask app.

    Args:
    ----
        app (Flask): The Flask application instance.

    """

    @app.after_request
    def set_secure_headers(response: Response) -> Response:
        """Set secure headers for the response.

        Args:
        ----
            response (Response): The Flask response object.

        Returns:
        -------
            Response: The modified response with secure headers.

        """
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


def configure_rate_limiting(app: Flask) -> None:
    """Configure rate limiting for the Flask app.

    Args:
    ----
        app (Flask): The Flask application instance.

    """
    limiter = Limiter(get_remote_address, app=app, default_limits=["100 per hour"])

    @app.route("/login")
    @limiter.limit("5 per minute")
    def login() -> str:
        """Handle login attempts with rate limiting.

        Returns
        -------
            str: A message indicating a login attempt.

        """
        return "Login attempt"


def configure_logging(app: Flask) -> None:
    """Configure logging for the Flask app.

    Args:
    ----
        app (Flask): The Flask application instance.

    """
    if not app.debug and not app.testing:
        logs_path = Path(__file__).resolve().parent.parent / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)
        log_file = logs_path / "ledgerbase.log"

        file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
        )
        file_handler.setFormatter(formatter)

        app.logger.addHandler(file_handler)
