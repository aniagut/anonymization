import cv2
import face_recognition
import os
import numpy as np

from keras.models import load_model
from tensorflow.keras.utils import img_to_array
from image_emotion_gender_demo import read_emotions

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

emotion_model_path = 'best_model.h5'

emotion_classifier = load_model(emotion_model_path, compile=False)
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised",
            "neutral"]


def analyze_emotions_on_photo(filename):
    path = os.path.join("processing", filename)
    photo, predicted_emotions = read_emotions(path)
    # photo = cv2.imread(path)
    #
    # face_locations = face_recognition.face_locations(photo)
    #
    # gray = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
    # predicted_emotions = {}
    #
    # for idx, (top, right, bottom, left) in enumerate(face_locations):
    #     cv2.rectangle(photo, (left, top), (right, bottom), (255, 255, 255), thickness=4)
    #     face = gray[top:bottom, left:right]
    #     face = cv2.resize(face, (224, 224))
    #     img_pixels = img_to_array(face)
    #     img_pixels = np.expand_dims(img_pixels, axis=0)
    #     img_pixels /= 255
    #
    #     predictions = emotion_classifier.predict(img_pixels)
    #     max_index = np.argmax(predictions[0])
    #     predicted_emotion = EMOTIONS[max_index]
    #     predicted_emotions[idx] = predicted_emotion
    #
    #     cv2.putText(photo, predicted_emotion, (int(left), int(top)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    #     cv2.putText(photo, f"id={idx}", (int(left), int(bottom)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    name, extension = os.path.splitext(filename)
    new_image_name = os.path.join("processing/emotions", f"{name}_processed{extension}")
    cv2.imwrite(new_image_name, photo)
    print(predicted_emotions)
    return predicted_emotions


def analyze_emotions_on_video(filename):
    path = os.path.join("processing", filename)
    video = cv2.VideoCapture(path)
    timestamps = []
    frames_list = []
    known_encodings = []
    emotions_list = {}
    fps = video.get(cv2.CAP_PROP_FPS)
    imageWidth = int(video.get(3))
    imageHeight = int(video.get(4))

    while video.isOpened():
        ret, frame = video.read()

        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        timestamps.append(video.get(cv2.CAP_PROP_POS_MSEC))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(frame)

        for idx, (top, right, bottom, left) in enumerate(face_locations):
            cv2.rectangle(frame, (left, top), (right, bottom), (255, 255, 255), thickness=4)
            face = gray[top:bottom, left:right]
            face = cv2.resize(face, (224, 224))

            face_encoding = face_encodings[idx]
            comparison = face_recognition.compare_faces(known_encodings, face_encoding)
            if True in comparison:
                folder_no = comparison.index(True)
            else:
                folder_no = len(known_encodings)
                known_encodings.append(face_encoding)

            img_pixels = img_to_array(face)
            img_pixels = np.expand_dims(img_pixels, axis=0)
            img_pixels /= 255

            predictions = emotion_classifier.predict(img_pixels)
            max_index = np.argmax(predictions[0])
            predicted_emotion = EMOTIONS[max_index]
            if emotions_list.get(folder_no) is not None:
                emotions_list[folder_no].append((predicted_emotion, timestamps[-1]))
            else:
                emotions_list[folder_no] = [(predicted_emotion, timestamps[-1])]

            cv2.putText(frame, predicted_emotion, (int(left), int(top)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, f"id={folder_no}", (int(left), int(bottom)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        frames_list.append(frame)
    video.release()

    name, extension = os.path.splitext(filename)
    new_video_name = os.path.join("processing/emotions", f"{name}_processed{extension}")
    videowriter = cv2.VideoWriter(new_video_name, cv2.VideoWriter_fourcc(*'DIVX'), fps, (imageWidth, imageHeight))

    for i in range(len(frames_list)):
        videowriter.write(frames_list[i])
    videowriter.release()

    clip = VideoFileClip(new_video_name)

    # loading audio file
    audioclip = AudioFileClip(path)

    # adding audio to the video clip
    videoclip = clip.set_audio(audioclip)

    # saving video clip
    new_video_sound_name = os.path.join("processing/emotions", f"{name}_processed_sound{extension}")
    videoclip.write_videofile(new_video_sound_name)

    cv2.destroyAllWindows()

    return emotions_list
