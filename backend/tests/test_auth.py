from similarity_webservice.auth import *


def test_missing_key(client):
    res = client.post("/api/collection/create", json={})
    assert res.status_code == 403


def test_wrong_key(client):
    res = client.post(
        "/api/collection/create", headers={"API-Key": "wrongkey"}, json={}
    )
    assert res.status_code == 403


def test_list_apikeys(apikey, app_context):
    keys = list_apikeys()
    assert len(keys) == 1
    key = keys[0]


def test_delete_apikey(apikey, app_context):
    delete_apikey(1)
    assert len(list_apikeys()) == 0


def test_list_keys(runner):
    result = runner.invoke(list)
    assert result.exit_code == 0
    assert "There are currently 0 active API keys" in result.output


def test_create_key(runner):
    result = runner.invoke(create, ["--name", "testkey"])
    assert result.exit_code == 0
    keys = list_apikeys()
    assert len(keys) == 1


def test_delete_key(runner, apikey):
    result = runner.invoke(delete, ["1"])
    assert result.exit_code == 0

    # Delete invalid apikey
    result = runner.invoke(delete, ["1"])
    assert result.exit_code == 0
