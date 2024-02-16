from similarity_webservice.app import create_app
from similarity_webservice.model import add_new_apikey, add_collection
from click.testing import CliRunner

import pytest


@pytest.fixture()
def app(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "SQLALCHEMY_DATABASE_URI", f"sqlite:///{str(tmp_path)}/similarity_webservice.db"
    )

    app = create_app()

    with app.app_context():
        # Add some sample data
        add_collection("collection1")
        add_collection("collection2")
        add_collection("collection3")

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def apikey(app):
    key = "testkey"
    with app.app_context():
        add_new_apikey("test", key)
    return key


@pytest.fixture()
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture()
def runner(app_context):
    return CliRunner()
