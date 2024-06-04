from similarity_webservice.vision import extract_features
from similarity_webservice.model import Images
import os
import torch
from PIL import Image
import time
import requests
import base64


def test_extract_features(app):
    from similarity_webservice.vision import model, vis_processors

    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
    # Test extract_features function
    raw_image_path = os.path.join(os.path.dirname(__file__), "dum_similarity_img.png")
    raw_image = Image.open(raw_image_path).convert("RGB")
    preprocessed_image = [vis_processors["eval"](raw_image).unsqueeze(0).to(device)]
    features = extract_features(preprocessed_image, model)

    assert isinstance(features, torch.Tensor)
    assert features.shape[0] == 1


def test_finetune(app, client, apikey):
    with app.app_context():
        # Retrieve the initial value of last_finetuned
        res = client.get("/api/collection/3/info")
        assert res.status_code == 200
        l_ft_b4 = res.json["last_finetuned"]

        res = client.post(
            "/api/collection/3/updatecontent",
            headers={"API-Key": apikey},
            data="https://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_1540/public/2021-06/dummyuser.png, https://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_1540/public/2021-06/dummyuser.png",
        )
        assert res.status_code == 200
        # Initiate the finetuning process
        res = client.post("/api/collection/3/finetune", headers={"API-Key": apikey})
        assert res.status_code == 200
        # Polling mechanism to wait for the finetuning process to complete
        max_poll_attempts = 10
        poll_interval_seconds = 5
        for _ in range(max_poll_attempts):
            # Retrieve the updated value of last_finetuned
            res = client.get("/api/collection/3/info")
            l_ft = res.json["last_finetuned"]

            # Check if the value has been updated
            if l_ft != l_ft_b4:
                break

            # Wait before polling again
            time.sleep(poll_interval_seconds)
        else:
            # If the loop completes without finding the updated value, raise an assertion error
            assert False, "Finetuning process did not complete within the expected time"

        # Check the difference between the last finetuned before and after finetuning
        assert l_ft != l_ft_b4

        img = Images.query.filter(Images.collection == 3).one()
        # Check if the parquet data was calculated
        assert img.parquet_data is not None


def test_similarity_search(app, client, apikey):
    with app.app_context():
        # Retrieve the initial value of last_finetuned
        res = client.get("/api/collection/3/info")
        assert res.status_code == 200
        l_ft_b4 = res.json["last_finetuned"]

        res = client.post(
            "/api/collection/3/updatecontent",
            headers={"API-Key": apikey},
            data="https://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_1540/public/2021-06/dummyuser.png, https://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_1540/public/2021-06/dummyuser.png\nhttps://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_3380/public/2023-04/liam_3582.jpeg,https://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_3380/public/2023-04/liam_3582.jpeg\nhttps://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_3380/public/2023-04/inga_3567.jpeg,https://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_3380/public/2023-04/inga_3567.jpeg",
        )
        assert res.status_code == 200
        # Initiate the finetuning process
        res = client.post("/api/collection/3/finetune", headers={"API-Key": apikey})
        assert res.status_code == 200

        # Polling mechanism to wait for the finetuning process to complete
        max_poll_attempts = 10
        poll_interval_seconds = 5
        for _ in range(max_poll_attempts):
            # Retrieve the updated value of last_finetuned
            res = client.get("/api/collection/3/info")
            l_ft = res.json["last_finetuned"]

            # Check if the value has been updated
            if l_ft != l_ft_b4:
                break

            # Wait before polling again
            time.sleep(poll_interval_seconds)
        else:
            # If the loop completes without finding the updated value, raise an assertion error
            assert False, "Finetuning process did not complete within the expected time"

        # get and encode test image
        response = requests.get(
            "https://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_3380/public/2023-04/dominic_3439.jpeg"
        )
        image_data = response.content
        encoded_image = base64.b64encode(image_data)

        res = client.post("/api/collection/3/search", data=encoded_image)
        # Check if the response is successful, and if the response contains the expected number of results
        assert res.status_code == 200
        assert len(res.json) > 0

        assert res.json[0]["score"] > 0.3
        assert res.json[1]["score"] > 0.3
        assert res.json[2]["score"] < 0.3

        assert (
            res.json[2]["image_url"]
            == "https://www.ssc.uni-heidelberg.de/sites/default/files/styles/img_free_aspect_1540/public/2021-06/dummyuser.png"
        )
