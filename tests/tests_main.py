
"""
Author: Colby Adams
Program: tests_main.py
Purpose: Tests if the Flask home page loads successfully.
"""

import pytest
import main


# Set up a temporary database for testing
@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "test.db"
    monkeypatch.setattr(main, "DATABASE", str(test_database))

    main.app.config["TESTING"] = True
    main.init_db()

    return main.app.test_client()


# Test if the home page loads successfully
def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Add Contact" in response.data

