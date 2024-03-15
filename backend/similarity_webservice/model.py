from similarity_webservice.heidicon import extract_heidicon_content

from datetime import datetime, timezone
from typing import Optional

import argon2
import csv
import dataclasses
import flask
import flask_sqlalchemy
import functools
import io

import torch
from lavis.models import load_model_and_preprocess

ph = argon2.PasswordHasher()
db = flask_sqlalchemy.SQLAlchemy()


def load_model_and_vis_preprocess():
    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
    model, vis_processors, _ = load_model_and_preprocess(
        name="blip2_feature_extractor",
        model_type="coco",
        is_eval=True,
    )
    model.to(device)
    return model, vis_processors


@dataclasses.dataclass
class Images(db.Model):
    """A data collection used in similarity search."""

    id: int = db.Column(db.Integer, primary_key=True)
    collection: int = db.Column(db.Integer)
    content: list = db.Column(db.JSON, nullable=False)
    parquet_data: bytes = db.Column(db.LargeBinary, nullable=True)


def images_as_csv(id: int):
    """Return the content of a collection as a CSV file."""

    images = Images.query.where(Images.collection == id).one()

    # Write the content into a string buffer
    with io.StringIO() as output:
        writer = csv.writer(output)
        writer.writerows(images.content)

        # Make this a binary buffer for flask
        mem = io.BytesIO()
        mem.write(output.getvalue().encode("utf-8"))
        mem.seek(0)

        return mem


@dataclasses.dataclass
class Collection(db.Model):
    """A data collection used in similarity search."""

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.Text, nullable=False)
    last_modified: datetime = db.Column(db.DateTime, nullable=False)
    last_finetuned: datetime = db.Column(db.DateTime)
    heidicon_tag: str = db.Column(db.Text, nullable=True)


def add_collection(name: str, heidicon_tag: Optional[str] = None):
    """Add a new collection to the database."""

    # Create the collection in the Collection table
    coll = Collection(
        name=name,
        last_modified=datetime.now(timezone.utc),
        last_finetuned=None,
        heidicon_tag=heidicon_tag,
    )
    db.session.add(coll)
    db.session.commit()

    # If a HeidICON tag was given, extract the content from HeidICON
    content = []
    if heidicon_tag is not None:
        content = extract_heidicon_content(heidicon_tag)

    # Add a corresponding entry in the Images table
    images = Images(collection=coll.id, content=content)
    db.session.add(images)
    db.session.commit()

    return coll


def delete_collection(id: int):
    """Delete a collection from the database."""

    coll = Collection.query.where(Collection.id == id).one()
    db.session.delete(coll)
    db.session.commit()


def update_collection_content(id: str, content: str):
    """Update the content of a given collection."""

    # If this is based on HeidICON, extract the content
    coll = Collection.query.where(Collection.id == id).one()
    if coll.heidicon_tag is not None:
        content = extract_heidicon_content(coll.heidicon_tag)
    else:
        # Normalize the given string input
        content = [
            [token.strip() for token in line.split(",")]
            for line in content.strip().split("\n")
        ]

    # Update the content of the collection
    images = Images.query.where(Images.collection == id).one()
    images.content = content

    # Update the last modified timestamp
    coll.last_modified = datetime.now(timezone.utc)
    db.session.commit()


def update_collection_name(id: str, name: str):
    """Update the name of a given collection."""

    coll = Collection.query.where(Collection.id == id).one()
    coll.name = name
    db.session.commit()


def list_collections():
    """List all collections."""

    return Collection.query.all()


def collection_info(id):
    """Get information about a collection."""

    # Get the data from the Collection and Images table
    coll = Collection.query.where(Collection.id == id).one()
    images = Images.query.where(Images.collection == id).one()

    # Convert to a dictionary and remove the SQLAlchemy state
    info = coll.__dict__
    info.pop("_sa_instance_state")

    # Add some derived information
    info["number_of_images"] = len(images.content)
    info["requires_finetuning"] = coll.last_modified > coll.last_finetuned
    return info


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
            return (
                flask.jsonify(message="API key is missing", message_type="error"),
                403,
            )

        # Verify API key (assuming it's hashed in the database)
        for keyobj in ApiKey.query.all():
            try:
                if ph.verify(keyobj.key, api_key):
                    # argon2 specifies that we need to occasionally rehash the password
                    if ph.check_needs_rehash(keyobj.key):
                        keyobj.key = ph.hash(api_key)
                        db.session.commit()

                    # Proceed with the original route function
                    return f(*args, **kwargs)
            except argon2.exceptions.VerifyMismatchError:
                pass

        # If we reach this point, the API key was not found
        return flask.jsonify(message="Invalid API key", message_type="error"), 403

    return decorated_function


def add_new_apikey(name: str, key: str) -> None:
    """Add a new API key to the database."""

    db.session.add(
        ApiKey(name=name, key=ph.hash(key), created=datetime.now(timezone.utc))
    )
    db.session.commit()


def list_apikeys() -> list[ApiKey]:
    """List all API keys."""

    return ApiKey.query.all()


def delete_apikey(id: int) -> None:
    """Delete an API key from the database."""

    key = ApiKey.query.where(ApiKey.id == id).one()
    db.session.delete(key)
    db.session.commit()
