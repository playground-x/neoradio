"""
Pytest configuration and fixtures for NeoRadio tests.
"""

import pytest
import os
import tempfile
from app import app, init_db, DATABASE


@pytest.fixture
def test_app():
    """Create and configure a test Flask application instance."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()

    # Configure app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path

    # Override the DATABASE constant for this test
    import app as app_module
    original_db = app_module.DATABASE
    app_module.DATABASE = db_path

    # Initialize the test database
    init_db()

    yield app

    # Cleanup - ensure all connections are closed
    import sqlite3
    import gc
    gc.collect()  # Force garbage collection to close any lingering connections

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        # On Windows, sometimes the file is still locked
        import time
        time.sleep(0.1)
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # If it still fails, the temp file will be cleaned up by OS

    app_module.DATABASE = original_db


@pytest.fixture
def client(test_app):
    """Create a test client for the Flask application."""
    return test_app.test_client()


@pytest.fixture
def runner(test_app):
    """Create a test CLI runner."""
    return test_app.test_cli_runner()
