from similarity_webservice.model import (
    db,
    require_api_key,
    add_collection,
    collection_info,
    list_collections,
    delete_collection,
    update_collection_content,
    update_collection_name,
    images_as_csv,
    load_model_and_vis_preprocess,
)
from similarity_webservice.vision import finetune_model, similarity_search

import base64
import flask
import flask_cors
import logging
import os
import sqlalchemy


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

    # Enable CORS for all routes
    flask_cors.CORS(app)

    # Initialize the database
    db.init_app(app)

    model, vis_processors = load_model_and_vis_preprocess()

    @app.route("/api/verify", methods=["POST"])
    @require_api_key
    def route_verify():
        return flask.jsonify(message="API key is valid", message_type="push")

    @app.route("/api/collection/create", methods=["POST"])
    @require_api_key
    def route_create_collection():
        data = flask.request.json

        if "name" not in data:
            return flask.jsonify(message="Name is missing", message_type="error"), 400

        # The frontend might send the empty string instead of null
        heidicon_tag = data.get("heidicon_tag", "")
        if heidicon_tag == "":
            heidicon_tag = None

        coll = add_collection(data["name"], heidicon_tag=heidicon_tag)
        return (
            flask.jsonify(
                message="Collection created", message_type="push", id=coll.id
            ),
            200,
        )

    @app.route("/api/collection/<id>/delete", methods=["POST"])
    @require_api_key
    def route_delete_collection(id):
        try:
            delete_collection(id)
            return flask.jsonify(message="Collection deleted", message_type="push")
        except sqlalchemy.exc.NoResultFound:
            return (
                flask.jsonify(message="Collection not found", message_type="error"),
                400,
            )

    @app.route("/api/collection/list", methods=["GET"])
    def route_list_collections():
        return flask.jsonify({"ids": [coll.id for coll in list_collections()]})

    @app.route("/api/collection/<id>/csvfile", methods=["GET"])
    def route_csvfile_collections(id):
        try:
            return flask.send_file(
                images_as_csv(id),
                as_attachment=True,
                download_name=f"{collection_info(id).name}.csv",
                mimetype="text/csv",
            )
        except sqlalchemy.exc.NoResultFound:
            return (
                flask.jsonify(
                    message=f"Collection with id={id} not found", message_type="error"
                ),
                400,
            )

    @app.route("/api/collection/<id>/info", methods=["GET"])
    def route_info_collection(id):
        try:
            coll = collection_info(id)
            return flask.jsonify(coll)
        except sqlalchemy.exc.NoResultFound:
            return (
                flask.jsonify(
                    message=f"Collection with id={id} not found", message_type="error"
                ),
                400,
            )

    @app.route("/api/collection/<id>/updatecontent", methods=["POST"])
    @require_api_key
    def route_update_collection_content(id):
        try:
            update_collection_content(id, flask.request.data.decode("utf-8"))
        except sqlalchemy.exc.NoResultFound:
            return (
                flask.jsonify(
                    message=f"Collection with id={id} not found", message_type="error"
                ),
                400,
            )

        return flask.jsonify(message="Collection updated", message_type="push")

    @app.route("/api/collection/<id>/updatename", methods=["POST"])
    @require_api_key
    def route_update_collection_name(id):
        data = flask.request.json

        try:
            if "name" in data:
                update_collection_name(id, data["name"])
        except sqlalchemy.exc.NoResultFound:
            return (
                flask.jsonify(
                    message=f"Collection with id={id} not found", message_type="error"
                ),
                400,
            )

        return flask.jsonify(message="Collection updated", message_type="push")

    @app.route("/api/collection/<id>/finetune", methods=["POST"])
    @require_api_key
    def route_finetune_collection(id):
        try:
            finetune_model(id, model, vis_processors)
            return flask.jsonify(
                message="Model finetuning started", message_type="push"
            )
        except sqlalchemy.exc.NoResultFound:
            return (
                flask.jsonify(
                    message=f"Collection with id={id} not found", message_type="error"
                ),
                400,
            )

    @app.route("/api/collection/<id>/search", methods=["POST"])
    def route_search(id):
        # Extract the image from the request
        if b"," in flask.request.data:
            image = base64.b64decode(flask.request.data.decode("utf-8").split(",")[1])
        else:
            image = base64.b64decode(flask.request.data)

        return flask.jsonify(similarity_search(id, [image], model, vis_processors))

    with app.app_context():
        db.create_all()

    return app
