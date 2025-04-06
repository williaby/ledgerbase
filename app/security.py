import logging
import os
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def apply_secure_headers(app):
    @app.after_request
    def set_secure_headers(response):
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
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        return response

def configure_rate_limiting(app):
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per hour"]
    )

    @app.route("/login")
    @limiter.limit("5 per minute")
    def login():
        return "Login attempt"

def configure_logging(app):
    if not app.debug and not app.testing:
        logs_path = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(logs_path, exist_ok=True)
        log_file = os.path.join(logs_path, 'ledgerbase.log')
        file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=10)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LedgerBase startup')
