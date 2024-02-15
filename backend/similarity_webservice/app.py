from similarity_webservice.model import (
    db,
    require_api_key,
    add_collection,
    collection_info,
    list_collections,
    delete_collection,
    update_collection,
)
from similarity_webservice.vision import finetune_model, similarity_search

import flask
import logging
import os


def create_app():
    """Create the Flask app for similarity search webservice.

    This is wrapped into a function in order to allow modifications to
    environment variables from Python before the app is created.
    """

    # Create a logger instance for our server.
    logger = logging.getLogger("similarity_webservice")

    # Create the flask app that will returned by this function
    app = flask.Flask("similarity_webservice")

    # Extract the config from environment variables and inject it into falsk
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_URI", "sqlite:///similarity_webservice.db"
    )

    # Initialize the database
    db.init_app(app)

    @app.route("/api/collection/create", methods=["POST"])
    @require_api_key
    def route_create_collection():
        data = flask.request.json

        if "name" not in data:
            return flask.jsonify(message="Name is missing"), 400

        coll = add_collection(data["name"])
        return flask.jsonify(message="Collection created", id=coll.id), 200

    @app.route("/api/collection/delete", methods=["DELETE"])
    @require_api_key
    def route_delete_collection():
        data = flask.request.json

        if "id" not in data:
            return flask.jsonify(message="ID is missing"), 400

        delete_collection(data["id"])
        return flask.jsonify(message="Collection deleted")

    @app.route("/api/collection/list", methods=["GET"])
    def route_list_collections():
        return flask.jsonify([coll.id for coll in list_collections()])

    @app.route("/api/collection/info", methods=["GET"])
    def route_info_collection():
        id = flask.request.args.get("id")
        coll = collection_info(id)
        return flask.jsonify(coll)

    @app.route("/api/collection/update", methods=["PUT"])
    @require_api_key
    def route_update_collection():
        data = flask.request.json

        if "id" not in data:
            return flask.jsonify(message="ID is missing"), 400
        if "content" not in data:
            return flask.jsonify(message="Content is missing"), 400

        update_collection(data["id"], data["content"])
        return flask.jsonify(message="Collection updated")

    @app.route("/api/collection/finetune", methods=["POST"])
    @require_api_key
    def route_finetune_collection():
        data = flask.request.json

        if "id" not in data:
            return flask.jsonify(message="ID is missing"), 400

        finetune_model(data["id"])
        return flask.jsonify(message="Model finetuning started")

    @app.route("/api/search", methods=["GET"])
    def route_search():
        # Extract the image from the request
        if "image" not in flask.request.files:
            return flask.jsonify(message="Image is missing"), 400
        image = flask.request.files["image"]

        # Extract relevant data from the request
        data = flask.request.json
        if "id" not in data:
            return flask.jsonify(message="ID is missing"), 400
        id = flask.request.json["id"]

        return flask.jsonify(similarity_search(id, image))

    with app.app_context():
        db.create_all()

    return app
