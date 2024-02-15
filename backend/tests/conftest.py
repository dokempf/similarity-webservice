from similarity_webservice.app import create_app, add_routes
from similarity_webservice.model import add_new_apikey

import pytest


@pytest.fixture()
def app(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "SQLALCHEMY_DATABASE_URI", f"sqlite://{str(tmp_path)}/similarity_webservice.db"
    )

    app = create_app()
    add_routes(app)
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
