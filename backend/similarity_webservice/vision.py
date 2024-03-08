import torch
from PIL import Image
import lavis
from datetime import datetime, timezone
from lavis.models import load_model_and_preprocess
from similarity_webservice.model import Images, Collection
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
    images = Images.query.filter(Images.collection == id).one()

    # For each image of collection we check if images do not have a parquet file, extract features for particular image and save them
    rows_with_missing_data = Images.query.filter(Images.parquet_data.is_(None)).all()

    # Perform actions on rows with missing data
    for row in rows_with_missing_data:
   
        raw_images = [Image.open(urllib.request.urlopen(image[0])).convert("RGB") for image in images.content]
        preprocessed_image = [
            vis_processors["eval"](raw_image).unsqueeze(0).to(device)
            for raw_image in raw_images
        ]
        features_image_stacked = extract_features(preprocessed_image, model)

        # Convert features to DataFrame and save to Parquet
        features_df = pd.DataFrame(features_image_stacked.cpu().numpy())
        parquet_file = io.BytesIO()
        features_df.to_parquet(parquet_file)
        parquet_file.seek(0)

        # Update the database with the extracted features
        images.parquet_data = parquet_file.read()
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
        vis_processors["eval"](Image.open(img).convert("RGB")).unsqueeze(0).to(device)
        for img in images
    ]
    multi_features_stacked = extract_features(preprocessed_image, model)

    # Load features for the collection from the database
    images_data = Images.query.filter(Images.collection == id).one()
    feature_df = pd.read_parquet(io.BytesIO(images_data.parquet_data))
    features_tensor = torch.tensor(feature_df.values).to(device)
    feature_df["id"] = images_data.id

    # calculate similarity scores, filter and sort them
    similarity_scores = torch.matmul(
        features_tensor, multi_features_stacked.unsqueeze(-1)
    ).squeeze()

    similar_image_indices = torch.nonzero(
        similarity_scores >= precision_thr, as_tuple=False
    ).squeeze()

    sorted_indices = sorted(
        similar_image_indices.tolist(), key=lambda x: similarity_scores[x], reverse=True
    )

    # Get the IDs of the most similar images
    most_similar_image_ids = [feature_df.iloc[i]["id"] for i in sorted_indices]
    return most_similar_image_ids[:num_limit]
