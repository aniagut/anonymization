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

import cv2
rgb_image = cv2.imread("img.jpg")
bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
cv2.imwrite("gray.jpg", bgr_image)