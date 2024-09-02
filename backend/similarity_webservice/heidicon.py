import requests


def _identify_tag_id(tag_info: list, target_tag: str):
    """Identify the ID of a tag from a list of tags."""

    # Go through the given tags and look for matches
    for tag in tag_info:
        # Recures into tag groups
        if tag["_basetype"] == "taggroup":
            recurse_id = _identify_tag_id(tag["_tags"], target_tag)
            if recurse_id is not None:
                return recurse_id
            else:
                continue

        # If the tag matches the display name in some language, return the ID
        if target_tag in tag["tag"]["displayname"].values():
            return tag["tag"]["_id"]

        # Maybe we passed the actual ID of the tag
        if target_tag == str(tag["tag"]["_id"]):
            return tag["tag"]["_id"]


def extract_heidicon_content(heidicon_tag: str):
    """Extract content from EasyDB."""

    # Set the EasyDB instance URL
    easydb_url = "https://heidicon.ub.uni-heidelberg.de"

    # Get a session token
    token = requests.get(f"{easydb_url}/api/session").json()["token"]

    # Authenticate the session token (as an anonymous user)
    requests.post(
        f"{easydb_url}/api/session/authenticate",
        params={"method": "anonymous", "token": token},
    )

    # Receive the tags that exist on the instance
    tags = requests.get(f"{easydb_url}/api/tags", params={"token": token}).json()

    # Identify the ID of the tag we want to extract
    tag_id = _identify_tag_id(tags, heidicon_tag)

    # The results data structure
    content = []

    # We access the EasyDB API in batches of 1000 objects
    offset = 0
    while offset % 1000 == 0:
        # Search for objects with the given tag
        objects = requests.get(
            f"{easydb_url}/api/search",
            params={"token": token},
            json={
                "search": [
                    {
                        "type": "in",
                        "bool": "must",
                        "fields": ["_tags._id"],
                        "in": [
                            tag_id,
                        ],
                    }
                ],
                "offset": offset,
                "limit": 1000,
            },
        ).json()

        # Iterate through the objects that we found
        for resource in objects["objects"]:
            for asset in resource["ressourcen"]["asset"]:
                for version in ["full", "huge", "small"]:
                    if version not in asset["versions"]:
                        continue

                    version_info = asset["versions"][version]
                    if version_info.get("_not_allowed", False) or not version_info.get(
                        "_download_allowed", True
                    ):
                        continue

                    # Some assets are "failed" or "pending". We cannot use them.
                    if version_info["status"] != "done":
                        continue

                    content.append(
                        (
                            version_info["download_url"],
                            f"{easydb_url}/#/detail/{resource['_system_object_id']}",
                        )
                    )
                    break

        # Set up the next batch. If the current batch was smaller than 1000,
        # we are done and can break out of the loop
        offset += len(objects["objects"])

    return content
