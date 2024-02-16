from similarity_webservice.auth import *


def test_missing_key(client):
    res = client.post("/api/collection/create", json={})
    assert res.status_code == 403


def test_list_apikeys(apikey, app_context):
    keys = list_apikeys()
    assert len(keys) == 1
    key = keys[0]


def test_delete_apikey(apikey, app_context):
    delete_apikey(1)
    assert len(list_apikeys()) == 0
