from datetime import datetime

import argon2
import dataclasses
import flask
import flask_sqlalchemy
import functools

ph = argon2.PasswordHasher()
db = flask_sqlalchemy.SQLAlchemy()


@dataclasses.dataclass
class Collection(db.Model):
    """A data collection used in similarity search."""

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.Text, nullable=False)
    last_modified: datetime = db.Column(db.DateTime, nullable=False)
    last_finetuned: datetime = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Collection {self.name}>"


def add_collection(name: str):
    """Add a new collection to the database."""
    coll = Collection(
        name=name, last_modified=datetime.now(datetime.UTC), last_finetuned=None
    )
    db.session.add(coll)
    db.session.commit()

    return coll.id


@dataclasses.dataclass
class ApiKey(db.Model):
    """An API key that can be used to access the similarity webservice."""

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.Text, nullable=False)
    key: str = db.Column(db.Text, nullable=False)
    created: datetime = db.Column(db.DateTime, nullable=False)


def require_api_key(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = flask.request.headers.get("API-Key")
        if api_key is None:
            return flask.jsonify({"message": "API key is missing"}), 403

        # Verify API key (assuming it's hashed in the database)
        try:
            # Query the database for the API key
            ApiKey.query.filter_by(hashed_key=ph.hash(api_key)).one()
        # TODO: Check what is raised and restrict to exactly that
        except:
            return flask.jsonify({"message": "Invalid API key"}), 403

        return f(*args, **kwargs)

    return decorated_function


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
