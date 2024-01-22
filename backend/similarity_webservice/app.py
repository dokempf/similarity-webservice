from similarity_webservice.model import db, require_api_key

import flask
import logging


# Create a logger instance for our server.
logger = logging.getLogger("similarity_webservice")

# Create the flask app that will returned by this function
app = flask.Flask("similarity_webservice")

# Extract the config from environment variables and inject it into falsk
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///similarity_webservice.db"

# Initialize the database
db.init_app(app)


@app.route("/api/collection/create", methods=["POST"])
@require_api_key
def create_collection():
    raise NotImplementedError()


@app.route("/api/collection/delete", methods=["DELETE"])
@require_api_key
def delete_collection():
    raise NotImplementedError()


@app.route("/api/collection/list", methods=["GET"])
def list_collections():
    raise NotImplementedError()


@app.route("/api/collection/update", methods=["PUT"])
@require_api_key
def update_collection():
    raise NotImplementedError()


@app.route("/api/collection/finetune", methods=["POST"])
@require_api_key
def finetune_collection():
    raise NotImplementedError()


@app.route("/api/search", methods=["GET"])
def search():
    raise NotImplementedError()


with app.app_context():
    db.create_all()
