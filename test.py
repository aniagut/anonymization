# import streamlit_authenticator as stauth
#
# hashed_passwords = stauth.Hasher(['123', '456']).generate()
# print(hashed_passwords)

# from gaze_tracking import GazeTracking
# import cv2
# frame = cv2.imread("img.jpg")
# gaze = GazeTracking()
# gaze.refresh(frame)
# print(gaze.is_center())
# new_frame = gaze.annotated_frame()
# print(gaze.horizontal_ratio())
# print(gaze.vertical_ratio())
# cv2.imwrite("gaze.jpg", new_frame)

# import boto3
#
# session = boto3.session.Session()
#
# client = session.client()

from deep_privacy import build_anonymizer
import pathlib
available_models = [
    "fdf128_rcnn512",
    "fdf128_retinanet512",
    "fdf128_retinanet256",
    "fdf128_retinanet128",
    "deep_privacy_V1",
]

anonymizer = build_anonymizer(model_name=available_models[4])
i_path = pathlib.Path("110619032504.jpg")
o_path = pathlib.Path("anon4.jpg")
anonymizer.anonymize_image_paths([i_path], [o_path])