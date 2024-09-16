from datetime import datetime, timezone
import torch
from PIL import Image
from similarity_webservice.model import db, Images, Collection, record_progress
import urllib.request
import pandas as pd
import io
from lavis.models import load_model_and_preprocess


# Storage for the singleton model and vis_processors
model = None
vis_processors = None


def load_model_and_vis_preprocess():
    global model, vis_processors

    if model is None:
        device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
        model, vis_processors, _ = load_model_and_preprocess(
            name="blip2_feature_extractor",
            model_type="coco",
            is_eval=True,
        )
        model.to(device)


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

    global model, vis_processors
    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
    row_with_data = Images.query.filter(Images.collection == id).one()
    coll = Collection.query.filter(Collection.id == id).one()
    content_list = row_with_data.content
    actual_content = []

    if row_with_data.parquet_data is None or (coll.last_modified > coll.last_finetuned):
        record_progress(id, 0)

        if row_with_data.parquet_data is None:
            parquet_df = pd.DataFrame()
            parquet_feature_tensor = torch.empty(0).to(device)
        else:
            parquet_df = pd.read_parquet(io.BytesIO(row_with_data.parquet_data))
            parquet_feature_tensor = torch.tensor(parquet_df.values).to(device)

        for i, content in enumerate(content_list):
            try:
                raw_image = Image.open(urllib.request.urlopen(content[0])).convert(
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

                actual_content.append(content)
                record_progress(id, int((i + 1) / len(content_list) * 100))
            except urllib.error.URLError:
                print(f"Could not download image {content[0]}")

        all_feature_df = pd.DataFrame(parquet_feature_tensor.cpu().numpy())
        parquet_file = io.BytesIO()
        all_feature_df.to_parquet(parquet_file)
        parquet_file.seek(0)

        row_with_data.parquet_data = parquet_file.read()
        row_with_data.content = actual_content

        coll.finetuning_progess = None
        coll.last_finetuned = datetime.now(timezone.utc)
        db.session.commit()


def similarity_search(id: str, images: list, num_limit=5, precision_thr=0.0):
    """Search for similar images in a given collection."""

    global model, vis_processors
    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
    preprocessed_image = [
        vis_processors["eval"](Image.open(io.BytesIO(img)).convert("RGB"))
        .unsqueeze(0)
        .to(device)
        for img in images
    ]
    multi_features_stacked = extract_features(preprocessed_image, model)

    # Load features for the collection from the database
    images_data = Images.query.filter(Images.collection == id).one()

    if images_data.parquet_data is not None:
        feature_df = pd.read_parquet(io.BytesIO(images_data.parquet_data))
        features_tensor = torch.tensor(feature_df.values).to(device)
    else:
        return

    # calculate similarity scores, filter and sort them
    similarity_scores = torch.matmul(
        features_tensor, multi_features_stacked.unsqueeze(-1)
    ).squeeze()
    if len(feature_df) == 1:
        return [
            {
                "image_url": images_data.content[0][0],
                "repo_url": images_data.content[0][1],
                "score": similarity_scores.item(),
            }
        ]

    similar_image_indices = torch.nonzero(
        similarity_scores >= precision_thr, as_tuple=True
    )
    sorted_indices = sorted(
        similar_image_indices[0], key=lambda x: similarity_scores[x], reverse=True
    )

    # Get the IDs of the most similar images
    most_similar_images = []
    for i in sorted_indices[:num_limit]:
        most_similar_images.append(
            {
                "image_url": images_data.content[i][0],
                "repo_url": images_data.content[i][1],
                "score": similarity_scores[i].item(),
            }
        )

    return most_similar_images
