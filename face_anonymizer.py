from deep_privacy.build import build_anonymizer
import os
import pathlib


def anonymize_video(filename, id, bucket, option):
    name, extension = os.path.splitext(filename)
    input_path = f"processing/{id}{extension}"
    blob = bucket.blob(input_path)
    blob.download_to_filename(f"tmp/{id}{extension}")
    output_path = f"tmp/anonymization/{id}{extension}"
    anonymizer = build_anonymizer(model_name=option)
    i_path = pathlib.Path(f"tmp/{id}{extension}")
    o_path = pathlib.Path(output_path)
    anonymizer.anonymize_video(i_path, o_path)
    blob = bucket.blob(f"processing/anonymization/{id}{extension}")
    blob.upload_from_filename(output_path)


def anonymize_photo(filename, id, bucket, option):
    name, extension = os.path.splitext(filename)
    input_path = f"processing/{id}{extension}"
    blob = bucket.blob(input_path)
    blob.download_to_filename(f"tmp/{id}{extension}")
    output_path = f"tmp/anonymization/{id}{extension}"
    anonymizer = build_anonymizer(model_name=option)
    i_path = pathlib.Path(f"tmp/{id}{extension}")
    o_path = pathlib.Path(output_path)
    anonymizer.anonymize_image_paths([i_path], [o_path])
    blob = bucket.blob(f"processing/anonymization/{id}{extension}")
    blob.upload_from_filename(output_path)