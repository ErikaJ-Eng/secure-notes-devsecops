"""Pruebas unitarias mínimas para el pipeline CI."""
import os
import sys

# Asegura que la app use SQLite en memoria durante los tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest  # noqa: E402
from app import app, db  # noqa: E402


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_create_and_list_note(client):
    resp = client.post("/api/notes", json={"title": "Hola", "content": "Mundo"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Hola"

    resp = client.get("/api/notes")
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_create_note_validation(client):
    resp = client.post("/api/notes", json={"title": "", "content": ""})
    assert resp.status_code == 400


def test_delete_missing_note(client):
    resp = client.delete("/api/notes/99999")
    assert resp.status_code == 404
