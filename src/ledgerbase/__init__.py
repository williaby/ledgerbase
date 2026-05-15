import os

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.flask import FlaskIntegration

from flask import Flask

from .error_handlers import register_error_handlers
from .security import (
    apply_secure_headers,
    configure_logging,
    configure_rate_limiting,
)

# Load environment variables from .env file
load_dotenv()

# Initialize SQLAlchemy instance (app-bound later)
db = SQLAlchemy()

# Conditionally initialize Sentry for error monitoring
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
        environment=os.getenv("FLASK_ENV", "development"),
    )
else:
    print("SENTRY_DSN not found, Sentry not initialized.")


def create_app() -> Flask:
    """Application factory function."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_dir = os.path.join(project_root, "templates")

    if not os.path.isdir(template_dir):
        print(f"Warning: Template directory not found at {template_dir}")
        app = Flask(__name__)
    else:
        app = Flask(__name__, template_folder=template_dir)

    flask_env = os.getenv("FLASK_ENV", "development").lower()
    is_production = flask_env == "production"

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        if is_production:
            raise ValueError("DATABASE_URL environment variable is not set.")
        database_url = "sqlite:///default.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        if is_production:
            raise ValueError("SECRET_KEY environment variable is not set.")
        secret_key = os.urandom(32).hex()
    app.config["SECRET_KEY"] = secret_key

    if is_production:
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
        app.config["PREFERRED_URL_SCHEME"] = "https"

    db.init_app(app)
    apply_secure_headers(app)
    configure_rate_limiting(app)
    configure_logging(app)
    register_error_handlers(app)

    @app.route("/")
    def index() -> str:
        return "LedgerBase API is running."

    if not is_production:
        @app.route("/debug-sentry")
        def trigger_error() -> str:
            result = 1 / 0
            return f"This should never return. Result was {result}"

    return app
