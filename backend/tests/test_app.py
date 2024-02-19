def test_list_collections(client):
    res = client.get("/api/collection/list")
    assert res.status_code == 200
    assert tuple(res.json["ids"]) == (1, 2, 3)


def test_info_collection(client):
    for id in [1, 2, 3]:
        res = client.get(f"/api/collection/info?id={id}")
        assert res.status_code == 200
        assert res.json["id"] == id
        assert res.json["name"] == f"collection{id}"
        assert res.json["last_modified"] is not None
        assert res.json["last_finetuned"] is None


def test_info_collection_missing_id(client):
    res = client.get("/api/collection/info")
    assert res.status_code == 400


def test_create_collection(client, apikey):
    res = client.post(
        "/api/collection/create",
        json={"name": "newcollection"},
        headers={"API-Key": apikey},
    )
    assert res.status_code == 200
    assert res.json["id"] == 4

    res = client.get("/api/collection/list")
    assert res.status_code == 200
    assert tuple(res.json["ids"]) == (1, 2, 3, 4)


def test_create_collection_missing_name(client, apikey):
    res = client.post("/api/collection/create", headers={"API-Key": apikey}, json={})
    assert res.status_code == 400


def test_delete_collection(client, apikey):
    res = client.delete(
        "/api/collection/delete", json={"id": 1}, headers={"API-Key": apikey}
    )
    assert res.status_code == 200

    res = client.get("/api/collection/list")
    assert res.status_code == 200
    assert tuple(res.json["ids"]) == (2, 3)


def test_delete_collection_missing_id(client, apikey):
    res = client.delete("/api/collection/delete", headers={"API-Key": apikey}, json={})
    assert res.status_code == 400


def test_delete_collection_invalid_id(client, apikey):
    res = client.delete(
        "/api/collection/delete", json={"id": 700}, headers={"API-Key": apikey}
    )
    assert res.status_code == 400


def test_update_collection(client, apikey):
    res = client.put(
        "/api/collection/update",
        json={"id": 1, "content": ["new", "content"]},
        headers={"API-Key": apikey},
    )
    assert res.status_code == 200

    res = client.get("/api/collection/info?id=1")
    assert res.status_code == 200


def test_update_collection_missing_data(client, apikey):
    res = client.put("/api/collection/update", headers={"API-Key": apikey}, json={})
    assert res.status_code == 400

    res = client.put(
        "/api/collection/update", headers={"API-Key": apikey}, json={"id": 1}
    )
    assert res.status_code == 400

    res = client.put(
        "/api/collection/update", headers={"API-Key": apikey}, json={"content": ["bla"]}
    )
    assert res.status_code == 400


def test_update_collection_invalid_id(client, apikey):
    res = client.put(
        "/api/collection/update",
        json={"id": 700, "content": ["new", "content"]},
        headers={"API-Key": apikey},
    )
    assert res.status_code == 400


# Currently not yet implemented
# def test_finetune_collection(client, apikey):
#     res = client.post("/api/collection/finetune", json={"id": 1}, headers={"API-Key": apikey})


# Currently not yet implemented
# def test_search(client):
#     res = client.get("/api/search")
#     assert res.status_code == 200
