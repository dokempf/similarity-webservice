from dataclasses import dataclass
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

import argon2

ph = argon2.PasswordHasher()
db = SQLAlchemy()


@dataclass
class Collection(db.Model):
    """A data collection used in similarity search."""

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.Text, nullable=False)
    last_modified: datetime = db.Column(db.DateTime, nullable=False)
    last_finetuned: datetime = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Collection {self.name}>"


@dataclass
class ApiKey(db.Model):
    """An API key that can be used to access the similarity webservice."""

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.Text, nullable=False)
    key: str = db.Column(db.Text, nullable=False)
    created: datetime = db.Column(db.DateTime, nullable=False)


def add_new_apikey(name: str, key: str) -> None:
    """Add a new API key to the database."""
    db.session.add(
        ApiKey(name=name, key=ph.hash(key), created=datetime.datetime.now(datetime.UTC))
    )
    db.session.commit()


def list_apikeys() -> list[ApiKey]:
    """List all API keys."""

    return ApiKey.query.all()


def delete_apikey(id: int) -> None:
    """Delete an API key from the database."""

    key = ApiKey.query.filter_by(id=id)

    if key is None:
        raise ValueError(f"API key with id {id} does not exist.")

    key.delete()
    db.session.commit()
