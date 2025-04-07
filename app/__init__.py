import os

import sentry_sdk
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sentry_sdk.integrations.flask import FlaskIntegration

from app.error_handlers import register_error_handlers
from app.security import (
    apply_secure_headers,
    configure_logging,
    configure_rate_limiting,
)
from flask import Flask

# Assuming these functions are correctly typed in their respective files
# (e.g., def register_error_handlers(app: Flask) -> None:)
# Flask is already imported, needed for type hints

# Load environment variables
load_dotenv()

# Initialize Sentry for global exception monitoring
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:  # Only initialize if DSN is provided
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        # Consider making sample rate configurable via env var
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
        environment=os.getenv("FLASK_ENV", "development"),
        # Consider enabling performance monitoring if desired
        # enable_tracing=True
    )
else:
    print("SENTRY_DSN not found, Sentry not initialized.")


# Initialize SQLAlchemy instance (bound later in create_app)
# Can add type hint if needed elsewhere: db: SQLAlchemy = SQLAlchemy()
db = SQLAlchemy()


# Add return type annotation for the Flask app instance
def create_app() -> Flask:
    """Factory function to create and configure the Flask application."""
    # Resolve absolute path to templates directory at project root
    # Ensure this path is correct relative to your project structure
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_dir = os.path.join(project_root, "templates")

    # Initialize Flask app with external template directory
    # Check if template_folder exists, otherwise Flask might use default paths
    if not os.path.isdir(template_dir):
        print(f"Warning: Template directory not found at {template_dir}")
        # Decide fallback behavior: use default or raise error
        app = Flask(__name__)
    else:
        app = Flask(__name__, template_folder=template_dir)

    # Flask Config - Use app.config.from_mapping or separate config object for clarity
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///default.db"  # Provide a default fallback?
    )
    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise ValueError("DATABASE_URL environment variable is not set.")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Consider adding SECRET_KEY for session management if needed
    # app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

    # Middleware and extensions
    db.init_app(app)
    apply_secure_headers(app)
    configure_rate_limiting(app)
    configure_logging(app)
    register_error_handlers(app)

    # Health Check
    @app.route("/")
    # Add return type annotation (string)
    def index() -> str:
        """Basic health check endpoint."""
        return "LedgerBase API is running."

    # Sentry Error Trigger (for testing)
    @app.route("/debug-sentry")
    # Add return type annotation (string)
    def trigger_error() -> str:
        """Endpoint to intentionally raise an error for Sentry testing."""
        # This line will raise ZeroDivisionError before the return is reached
        result = 1 / 0
        return f"This should never return. Result was {result}"

    return app
