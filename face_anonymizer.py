from deep_privacy.build import build_anonymizer
import os
import pathlib
from keras.models import load_model

emotion_model_path = 'best_model.h5'

emotion_classifier = load_model(emotion_model_path, compile=False)
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised",
            "neutral"]

def anonymize_video(filename, id):
    path = os.path.join("processing", filename)
    name, extension = os.path.splitext(filename)
    output_path = os.path.join("processing/anonymization", f"{id}{extension}")
    anonymizer = build_anonymizer()
    i_path = pathlib.Path(path)
    o_path = pathlib.Path(output_path)
    anonymizer.anonymize_video(i_path, o_path)


def anonymize_photo(filename, id):
    path = os.path.join("processing", filename)
    name, extension = os.path.splitext(filename)
    output_path = os.path.join("processing/anonymization", f"{id}{extension}")
    i_path = pathlib.Path(path)
    o_path = pathlib.Path(output_path)
    anonymizer = build_anonymizer()
    anonymizer.anonymize_image_paths([i_path], [o_path])