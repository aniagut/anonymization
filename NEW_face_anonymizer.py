import cv2
import face_recognition
import os
import numpy as np
from process_data import get_lndm
from test import run_inference
from deep_privacy import build_anonymizer
import pathlib

def anonymize_photo(filename):
    photo = cv2.imread(filename)

    face_locations = face_recognition.face_locations(photo)
    path_in = os.path.join("processing/anonymization/img_in/")
    path_out = os.path.join("processing/anonymization/img_out/")
    os.mkdir(path_in)
    os.mkdir(path_out)

    for idx, (top, right, bottom, left) in enumerate(face_locations):
        face = photo[top:bottom, left:right]
        face = cv2.resize(face, (128,128))
        full_dir_path_in = path_in + str(idx)
        os.mkdir(full_dir_path_in)
        full_img_path_in = full_dir_path_in + "/000000.jpg"
        cv2.imwrite(full_img_path_in, face)
    get_lndm(path_in, path_out)
    path_anonymized = "processing/anonymization/anonymized"
    os.mkdir(path_anonymized)
    run_inference(data_path=path_out, model_path="modelG_ciagan", output_path=path_anonymized)


def anonymize_photo1():
    anonymizer = build_anonymizer()
    anonymizer.anonymize_image_paths([pathlib.Path("000001.jpg")], [pathlib.Path("00002.jpg")])
anonymize_photo1()