#!/usr/bin/env python3
"""
Source code: https://github.com/KichangKim/DeepDanbooru/issues/56#issuecomment-1100770505
"""
import pathlib
from typing import Any, List, Optional, Sequence, Tuple, Union
import click
import six
import deepdanbooru
from config import *

try:
    import tensorflow as tf
except ImportError:
    print("Tensorflow Import failed")
    tf = None


def load_tags(tags_path: Union[pathlib.Path, str, click.types.Path]):
    with open(tags_path, "r") as stream:  # type: ignore
        tags = [tag for tag in (tag.strip() for tag in stream) if tag]
    return tags


def load_model_and_tags(model_path, tags_path, compile_):
    print("loading model...")
    if compile_ is None:
        model = tf.keras.models.load_model(model_path)
    else:
        model = tf.keras.models.load_model(model_path, compile=compile_)
    print("loading tags...")
    tags = load_tags(tags_path)
    return model, tags


def eval(
    image_path: Union[six.BytesIO, str, click.types.Path],
    threshold: float,
    model: Optional[Any] = None,
    tags: Optional[List[str]] = None,
) -> Sequence[Union[str, Tuple[str, Any], None]]:

    return deepdanbooru.commands.evaluate_image(image_path, model, tags, threshold)


def get_model_and_tags():
    modelFile = MODEL_FILE
    tagsFile = TAGS_FILE
    model, tags = load_model_and_tags(modelFile, tagsFile, None)
    return model, tags


def get_tags_and_score(filePath, model, tags):
    if filePath.lower().endswith((".jpg", ".png", ".webp", ".jpeg")):  # , ".gif", ".bmp"
        try:
            return eval(
                filePath,
                0.6,
                model,
                tags,
            )
        except:
            return
