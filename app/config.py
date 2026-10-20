"""
Resume Parser - Application Configuration
==========================================
Reads environment variables from .env file and provides
configuration classes for the Flask application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/resume_parser_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
