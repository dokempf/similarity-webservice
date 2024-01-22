from similarity_webservice.database import db
from typing import Optional

import flask
import logging


def create_app(config_path: Optional[str] = None) -> flask.Flask:
    """Create the flask app that will be used to run the similarity webservice."""

    # Create a logger instance for our server.
    logger = logging.getLogger("similarity_webservice")

    # Create the flask app that will returned by this function
    app = flask.Flask("similarity_webservice")

    # Extract the config from environment variables and inject it into falsk
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///similarity_webservice.db"

    # Initialize the database
    db.init_app(app)

    @app.route("/api/collection/create", methods=["POST"])
    def create_collection():
        raise NotImplementedError()

    @app.route("/api/collection/delete", methods=["DELETE"])
    def delete_collection():
        raise NotImplementedError()

    @app.route("/api/collection/list", methods=["GET"])
    def list_collections():
        raise NotImplementedError()

    @app.route("/api/collection/update", methods=["PUT"])
    def update_collection():
        raise NotImplementedError()

    @app.route("/api/collection/finetune", methods=["POST"])
    def finetune_collection():
        raise NotImplementedError()

    @app.route("/api/search", methods=["GET"])
    def search():
        raise NotImplementedError()

    with app.app_context():
        db.create_all()

    return app
