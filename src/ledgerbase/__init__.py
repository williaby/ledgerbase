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

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///default.db"
    )
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise ValueError("DATABASE_URL environment variable is not set.")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-secret-key")

    # Initialize core services and middleware
    db.init_app(app)
    apply_secure_headers(app)
    configure_rate_limiting(app)
    configure_logging(app)
    register_error_handlers(app)

    @app.route("/")
    def index() -> str:
        return "LedgerBase API is running."

    @app.route("/debug-sentry")
    def trigger_error() -> str:
        result = 1 / 0
        return f"This should never return. Result was {result}"

    return app
