from deep_privacy import build_anonymizer
import os
import pathlib


def anonymize_video(filename):
    path = os.path.join("processing", filename)
    name, extension = os.path.splitext(filename)
    output_path = os.path.join("processing/anonymization", f"{name}_processed{extension}")
    anonymizer = build_anonymizer()
    i_path = pathlib.Path(path)
    o_path = pathlib.Path(output_path)
    anonymizer.anonymize_video(i_path, o_path)


def anonymize_photo(filename):
    path = os.path.join("processing", filename)
    name, extension = os.path.splitext(filename)
    output_path = os.path.join("processing/anonymization", f"{name}_processed{extension}")
    i_path = pathlib.Path(path)
    o_path = pathlib.Path(output_path)
    anonymizer = build_anonymizer()
    anonymizer.anonymize_image_paths([i_path], [o_path])
