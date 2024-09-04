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
    startup_sanity_check,
)
from similarity_webservice.vision import (
    load_model_and_vis_preprocess,
    finetune_model,
    record_progress,
    similarity_search,
)

import base64
import flask
import flask_cors
import logging
import os
import sqlalchemy
import threading


def create_app(instantiate_model=True):
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

    # Lazily load the model and vis_processors
    if instantiate_model:
        load_model_and_vis_preprocess()

    # Enable CORS for all routes
    flask_cors.CORS(app)

    # Initialize the database
    db.init_app(app)

    @app.route("/api/verify", methods=["POST"])
    @require_api_key
    def route_verify():
        """Verify an API key.

        :reqheader API-Key: The API key to verify.
        :status 200: The API key is valid.
        :status 403: The API key is invalid.
        """
        return flask.jsonify(message="API key is valid", message_type="push")

    @app.route("/api/collection/create", methods=["POST"])
    @require_api_key
    def route_create_collection():
        """Create a new collection.

        :reqheader API-Key: The API key.
        :reqjson string name: The name of the collection to be created.
        :reqjson string heidicon_tag: The HeidICON tag to be associated with the collection, if this collection is managed through HeidICON.
        :status 200: The collection was created successfully.
        """
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
        """
        Delete a collection.

        :reqheader API-Key: The API key.
        :param id: The ID of the collection to delete.
        :status 200: The collection was deleted successfully.
        :status 400: The collection to delete was not found.
        """
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
        """
        List all existing collections.

        :resjson list ids: The list of collection IDs.
        :resjson list names: A list of objects for each collection, with properies value, id and name.
        :status 200: The list of collections was returned successfully.
        """
        coll_list = list_collections()
        return flask.jsonify(
            {
                "ids": [coll.id for coll in coll_list],
                "names": [
                    {"value": coll.id, "id": coll.id, "name": coll.name}
                    for coll in coll_list
                ],
            }
        )

    @app.route("/api/collection/<id>/csvfile", methods=["GET"])
    def route_csvfile_collections(id):
        """
        Download the CSV file for a collection.

        :param id: The ID of the collection to download the CSV file for.

        :status 200: The CSV file was downloaded successfully.
        :status 400: The collection to download the CSV file for was not found.
        """
        try:
            return flask.send_file(
                images_as_csv(id),
                as_attachment=True,
                download_name=f"{collection_info(id)['name']}.csv",
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
        """
        Get information about a collection.

        :param id: The ID of the collection to get information about.
        :resjson bool number_of_images: The number of images in the collection.
        :resjson bool requires_finetuning: Whether the collection requires finetuning.
        :resjson string name: The name of the collection.
        :resjson string last_modified: The date the collection was last modified.
        :resjson string last_finetuned: The date the collection was last finetuned.
        :resjson float finetuning_progess: The progress of the finetuning operation.
        :resjson string heidicon_tag: The HeidICON tag associated with the collection.
        :resjson int id: The ID of the collection.
        :status 200: The information about the collection was returned successfully.
        :status 400: The collection to get information about was not found.
        """
        try:
            return flask.jsonify(**collection_info(id))
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
        """
        Upload new content for a collection.

        Note that this currently does not allow incremental updates, but replaces the
        content of the collection. If you want to add images, download the CSV file
        with :http:get:`/api/collection/{id}/csvfile`, add the new images and upload the
        resulting CSV file.

        :reqheader API-Key: The API key.
        :param id: The ID of the collection to update.
        :reqjson string content: The new content of the collection as a base64 encoded string.
        :status 200: The collection was updated successfully.
        :status 400: The collection to update was not found.
        """
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
        """
        Change the name of a collection.

        :reqheader API-Key: The API key.
        :param id: The ID of the collection to update.
        :reqjson string name: The new name of the collection.
        :status 200: The collection was updated successfully.
        :status 400: The collection to update was not found.
        """
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
        """
        Finetune the model for a collection.

        This is a required process for the model to be usable in similarity search.
        Note, that the finetuning process takes a while to complete. Therefore,
        this route will return immediately after starting the finetuning process.
        You can then query the progress of the finetuning process with
        :http:get:`/api/collection/{id}/info`.

        :reqheader API-Key: The API key.
        :param id: The ID of the collection to finetune the model for.
        :status 200: The model finetuning was started successfully.
        """
        try:
            record_progress(id, 0)

            def _threaded_finetune_model(ctx, id):
                ctx.push()
                finetune_model(id)

            thread = threading.Thread(
                target=_threaded_finetune_model,
                args=(app.app_context(), id),
            )
            thread.daemon = True
            thread.start()
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
        """
        Perform a similarity search in a collection.

        :param id: The ID of the collection to search in.
        :reqjson string image: The image to search for as a base64 encoded string.
        :resjson list results: The list of results of the similarity search.
        :status 200: The similarity search was successful.
        :status 400: The collection to search in was not found.
        """
        # Extract the image from the request
        try:
            if b"," in flask.request.data:
                image = base64.b64decode(
                    flask.request.data.decode("utf-8").split(",")[1]
                )
            else:
                image = base64.b64decode(flask.request.data)

            return flask.jsonify(similarity_search(id, [image]))

        except sqlalchemy.exc.NoResultFound:
            return (
                flask.jsonify(
                    message=f"Collection with id={id} not found", message_type="error"
                ),
                400,
            )

    with app.app_context():
        db.create_all()
        startup_sanity_check()

    return app
