import torch
from PIL import Image
import lavis
from lavis.models import load_model_and_preprocess
from model import Images, Collection
import urllib.request
import pandas as pd
import numpy as np


def read_features_from_parquet(parquet_file):
    """
    Read features from a Parquet file and return them as a dictionary.
    """

    # Read the Parquet file
    features_df = pd.read_parquet(parquet_file)

    # Initialize an empty dictionary to store the features
    features_dict = {}

    # Iterate through the rows of the DataFrame
    for index, row in features_df.iterrows():
        # Get the ID and features from the row
        image_id = int(row["id"])
        features = row.drop("id").values

        # Convert the features to a PyTorch tensor
        features_tensor = torch.tensor(features, dtype=torch.float32)

        # Add the features to the dictionary
        features_dict[image_id] = features_tensor

    return features_dict


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
    images = Images.query.where(Images.collection == id).one()

    # Load the image tensors from file
    feature_dict = read_features_from_parquet(
        "/saved_features_image_stacked_col" + id + ".parquet"
    )

    # if image_id is not in the dictionary, then we should load, preprocess and extract features of the image
    for image in images:
        if image.id not in feature_dict:
            # Load image from the url using request lib  and preprocess it
            raw_image = Image.open(urllib.request.urlopen(image.content[0])).convert(
                "RGB"
            )

            preprocessed_image = [
                vis_processors["eval"](raw_image).unsqueeze(0).to(device)
            ]
            features = extract_features(preprocessed_image, model)

            # Save the updated image tensors to file
            feature_dict[image.id] = features.cpu().numpy().flatten()
    # Save the updated image tensors to file
    num_features = len(next(iter(feature_dict.values())))
    features_df = pd.DataFrame.from_dict(
        feature_dict,
        orient="index",
        columns=[f"feature_{i}" for i in range(num_features)],
    )
    features_df.insert(0, "id", list(feature_dict.keys()))
    features_df = features_df.applymap(
        lambda x: x.numpy() if isinstance(x, torch.Tensor) else x
    )
    features_df.to_parquet(
        "/saved_features_image_stacked_col" + id + ".parquet", index=False
    )


def similarity_search(id: str, images: list, num_limit=5, precision_thr=0.0):
    """Search for similar images in a given collection."""

    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
    model, vis_processors, _ = load_model_and_preprocess(
        name="blip2_feature_extractor",
        model_type="coco",
        is_eval=True,
    )
    model.to(device)
    # 1 upload and then preprocess images and collection features
    raw_images = [Image.open(image).convert("RGB") for image in images]
    preprocessed_image = [
        vis_processors["eval"](raw_image).unsqueeze(0).to(device)
        for raw_image in raw_images
    ]
    features_image_stacked = read_features_from_parquet(
        "/saved_features_image_stacked_col" + id + ".parquet"
    )
    multi_features_stacked = extract_features(preprocessed_image, model)

    features_tensor = torch.stack(list(features_image_stacked.values())).to(device)

    # 2 calculate similarity scores, filter and sort them
    similarity_scores = torch.matmul(
        features_tensor, multi_features_stacked.unsqueeze(-1)
    ).squeeze()

    most_similar_indices = torch.nonzero(
        similarity_scores >= precision_thr, as_tuple=False
    ).squeeze()

    id_to_index = {
        image_id: index for index, image_id in enumerate(features_image_stacked.keys())
    }

    most_similar_image_ids = [
        list(features_image_stacked.keys())[i] for i in most_similar_indices
    ]
    most_similar_image_ids = sorted(
        most_similar_image_ids,
        key=lambda x: similarity_scores[id_to_index[x]],
        reverse=True,
    )

    return most_similar_image_ids[:num_limit]
