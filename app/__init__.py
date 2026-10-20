"""
Resume Parser - Flask Application Factory
==========================================
Creates and configures the Flask application with:
- SQLAlchemy database connection
- Upload folder setup
- Blueprint registration (routes added in Phase 4)
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance (shared across modules)
db = SQLAlchemy()


def create_app():
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Load configuration
    from app.config import Config
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    # Ensure upload folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Register models (ensures tables are known to SQLAlchemy)
    with app.app_context():
        from app.models import Resume, Education, Experience, Project, Skill, User  # noqa: F401

        # Create all tables if they don't exist
        db.create_all()

    # Register routes blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app
