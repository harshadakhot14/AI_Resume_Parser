"""
Resume Parser - Application Entry Point
========================================
Run this file to start the Flask development server.

Usage:
    python run.py
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  Resume Parser - Starting Server")
    print("=" * 50)
    print(f"  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"  Upload Folder: {app.config['UPLOAD_FOLDER']}")
    print(f"  Max File Size: {app.config['MAX_CONTENT_LENGTH'] // (1024*1024)}MB")
    print("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)
