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
#
# from deep_privacy import build_anonymizer
# import pathlib
# available_models = [
#     "fdf128_rcnn512",
#     "fdf128_retinanet512",
#     "fdf128_retinanet256",
#     "fdf128_retinanet128",
#     "deep_privacy_V1",
# ]
#
# anonymizer = build_anonymizer(model_name=available_models[4])
# i_path = pathlib.Path("110619032504.jpg")
# o_path = pathlib.Path("anon4.jpg")
# anonymizer.anonymize_image_paths([i_path], [o_path])

from NEW_emotions_analyzer import analyze_emotions_on_photo, analyze_emotions_on_video

# print(analyze_emotions_on_video("trimmed3.mp4", "dc9fde7e-faab-4236-a470-cb137621eb2a"))
print(analyze_emotions_on_photo("2.jpg", "a971147e-aba2-4e31-a9e5-9bf8ad6ab097-2"))
# emotions_list = {0: [('happy', time1), ('sad', time2)], 1: [('happy', time1), ('sad', time2)], 2: [('happy', time1), ('sad', time2)], 3: [('happy', time1), ('sad', time2)], 4: [('happy', time1), ('sad', time2)]}

# for person, emotions in emotions_list.items():
    # wykres ilosci emocji w czasie
    # wykres zmiany w czasie

# import matplotlib.pyplot as plt
#
# x_axis = [0.034, 0.057, 1.56]
# y_axis = ['sad', 'happy', 'happy']
#
# plt.plot(x_axis, y_axis)
# plt.title('Person id')
# plt.xlabel('Timestamps')
# plt.ylabel('Emotions')
# plt.show()
#
# import matplotlib.pyplot as plt
# import numpy as np
#
# labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
# y = np.array([3, 25, 25, 15])
#
# plt.pie(y, labels=labels, autopct='%1.1f%%')
# plt.title("Person id")
# plt.show()

# from gaze_tracking import GazeTracking
#
# img_path = "abcdefg.png"
#
# gz = GazeTracking()
# import cv2
# img = cv2.imread(img_path)
#
# gz.refresh(img)
#
# print(gz.horizontal_ratio())
# print(gz.vertical_ratio())
# print(gz.is_center())
# print(gz.is_left())
# print(gz.is_right())
# print(gz.is_blinking())
# right 0 left 1 on horizontal
# up 0 down 1 on vertical

# wykresik : blinking, left-up, right-up, right-down, left-down, center-up, center-down, center-center,

from fpdf import FPDF