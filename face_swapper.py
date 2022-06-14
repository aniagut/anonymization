import cv2
import os
import numpy as np
import dlib
import time

def swap_face_on_image(filename_src, filename_dest):
    path_src = os.path.join("processing", filename_src)
    path_dest = os.path.join("processing", filename_dest)

    photo_src = cv2.imread(path_src)
    photo_dest = cv2.imread(path_dest)

    gray_src = cv2.cvtColor(photo_src, cv2.COLOR_BGR2RGB)
    gray_dest = cv2.cvtColor(photo_dest, cv2.COLOR_BGR2RGB)

    mask = np.zeros_like(gray_src)

    land_detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    source_face = land_detector(gray_src)

    for face in source_face:
        landmarks = predictor(gray_src, face)
        points = []
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            points.append((x, y))
        face_point = np.array(points, np.int32)
        convexhull = cv2.convexHull(face_point)

    dest_face = land_detector(gray_dest)
    for face in dest_face:
        landmarks = predictor(gray_dest, face)
        points2 = []
        for n in range(0, 68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            points2.append((x, y))