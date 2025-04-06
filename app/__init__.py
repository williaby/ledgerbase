import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app.security import (
    apply_secure_headers,
    configure_rate_limiting,
    configure_logging
)
from app.error_handlers import register_error_handlers

# Load environment variables
load_dotenv()

# Initialize Sentry for global exception monitoring
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("FLASK_ENV", "development")
)

# Initialize SQLAlchemy instance (bound later in create_app)
db = SQLAlchemy()

def create_app():
    # Resolve absolute path to templates directory at project root
    template_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "templates")
    )

    # Initialize Flask app with external template directory
    app = Flask(__name__, template_folder=template_dir)

    # Flask Config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Middleware and extensions
    db.init_app(app)
    apply_secure_headers(app)
    configure_rate_limiting(app)
    configure_logging(app)
    register_error_handlers(app)

    # Health Check
    @app.route("/")
    def index():
        return "LedgerBase API is running."

    # Sentry Error Trigger
    @app.route("/debug-sentry")
    def trigger_error():
        _ = 1 / 0  # Raise an intentional error for Sentry
        return "This should never return"

    return app
