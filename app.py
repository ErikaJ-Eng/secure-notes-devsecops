"""
Secure Notes API - Aplicación de demostración DevSecOps
"""

import logging
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("secure-notes")

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "cambia-esto-en-produccion",
)

database_url = os.environ.get("DATABASE_URL", "sqlite:///notes.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

Talisman(
    app,
    force_https=False,
    content_security_policy={
        "default-src": "'self'",
        "style-src": "'self' 'unsafe-inline'",
    },
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@app.route("/")
def index():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template("index.html", notes=notes)


@app.route("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "database": "up"}), 200
    except Exception as exc:
        logger.error("Health check fallido: %s", exc)
        return jsonify({"status": "error", "database": "down"}), 503


@app.route("/api/notes", methods=["GET"])
@limiter.limit("30 per minute")
def list_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notes]), 200


@app.route("/api/notes", methods=["POST"])
@limiter.limit("10 per minute")
def create_note():
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    content = (data.get("content") or "").strip()

    if not title or not content:
        return jsonify({"error": "title y content son obligatorios"}), 400

    if len(title) > 120:
        return jsonify({"error": "title supera 120 caracteres"}), 400

    note = Note(title=title, content=content)

    db.session.add(note)
    db.session.commit()

    logger.info("Nota creada id=%s", note.id)

    return jsonify(note.to_dict()), 201


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
@limiter.limit("10 per minute")
def delete_note(note_id):
    note = Note.query.get(note_id)

    if note is None:
        return jsonify({"error": "no encontrada"}), 404

    db.session.delete(note)
    db.session.commit()

    logger.info("Nota eliminada id=%s", note_id)

    return jsonify({"status": "eliminada"}), 200


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
