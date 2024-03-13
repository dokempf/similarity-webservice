from datetime import datetime, timezone
import torch
from PIL import Image
import lavis
from lavis.models import load_model_and_preprocess
from similarity_webservice.model import db, Images, Collection
import urllib.request
import pandas as pd
import numpy as np
import io


def extract_features(images: list, model):
    """
    Extract features from an image using the BLIP2 model.
    """

    image_tensor = torch.stack(images)
    features_image = [
        model.extract_features({"image": ten, "text_input": ""}, mode="image")
        for ten in image_tensor
    ]
    features_image_stacked = torch.stack(
        [feat.image_embeds_proj[:, 0, :].squeeze(0) for feat in features_image]
    )
    return features_image_stacked


def finetune_model(id: str):
    """Finetune a model with a given collection."""

    # The collection will be consist of the link to the image and for printing
    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
    model, vis_processors, _ = load_model_and_preprocess(
        name="blip2_feature_extractor",
        model_type="coco",
        is_eval=True,
    )
    model.to(device)
    # Fetch the URLs of the images from the database
    row_with_data = Images.query.filter(Images.collection == id).one()
    content_list = row_with_data.content

    if row_with_data.parquet_data is None or len(row_with_data.content) != len(
        pd.read_parquet(io.BytesIO(row_with_data.parquet_data))
    ):
        #Update finetune_time
        coll = Collection.query.filter(Collection.id == id).one()
        coll.last_finetuned = datetime.now(timezone.utc)
        db.session.commit()
        
        if row_with_data.parquet_data is None:
            parquet_df = pd.DataFrame()
            parquet_feature_tensor = torch.empty(0).to(device)
        else:
            parquet_df = pd.read_parquet(io.BytesIO(row_with_data.parquet_data))
            parquet_feature_tensor = torch.tensor(parquet_df.values).to(device)

        for i in range(len(parquet_df), len(content_list)):
            raw_image = Image.open(urllib.request.urlopen(content_list[i][0])).convert(
                "RGB"
            )
            preprocessed_image = [
                vis_processors["eval"](raw_image).unsqueeze(0).to(device)
            ]

            features_image_stacked = extract_features(preprocessed_image, model)
            # Concatenate extracted features
            parquet_feature_tensor = torch.cat(
                [parquet_feature_tensor, features_image_stacked]
            )

        all_feature_df = pd.DataFrame(parquet_feature_tensor.cpu().numpy())
        parquet_file = io.BytesIO()
        all_feature_df.to_parquet(parquet_file)
        parquet_file.seek(0)

        row_with_data.parquet_data = parquet_file.read()
        coll = Collection.query.filter(Collection.id == id).one()
        coll.last_finetuned = datetime.now(timezone.utc)
        db.session.commit()


def similarity_search(id: str, images: list, num_limit=5, precision_thr=0.0):
    """Search for similar images in a given collection."""

    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
    model, vis_processors, _ = load_model_and_preprocess(
        name="blip2_feature_extractor",
        model_type="coco",
        is_eval=True,
    )
    model.to(device)
    # preprocess upload images and calculate features
    preprocessed_image = [
        vis_processors["eval"](Image.open(io.BytesIO(img)).convert("RGB"))
        .unsqueeze(0)
        .to(device)
        for img in images
    ]
    multi_features_stacked = extract_features(preprocessed_image, model)
