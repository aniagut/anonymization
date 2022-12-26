import cv2
import face_recognition
import os
import numpy as np
from GazeTracking.gaze_tracking import GazeTracking

from keras.models import load_model
from tensorflow.keras.utils import img_to_array


from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

emotion_model_path = 'best_model.h5'

emotion_classifier = load_model(emotion_model_path, compile=False)
EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised",
            "neutral"]


def analyze_emotions_on_photo(filename, file_id, bucket):
    gaze = GazeTracking()
    name, extension = os.path.splitext(filename)
    input_path = f"processing/{id}{extension}"
    img_to_recognize = face_recognition.load_image_file(input_path)
    face_locations = face_recognition.face_locations(img_to_recognize)
    name, extension = os.path.splitext(filename)

    anonymized_path = os.path.join("tmp/anonymization", f"{file_id}{extension}")

    anonymized_photo = cv2.imread(anonymized_path)
    photo = cv2.imread(input_path)

    gray = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
    predicted_emotions = {}
    for idx, (top, right, bottom, left) in enumerate(face_locations):
        cv2.rectangle(anonymized_photo, (left, top), (right, bottom), (255, 255, 255), thickness=4)
        face = gray[top:bottom, left:right]
        facergb = photo[top:bottom, left:right]
        gaze.refresh(facergb)
        horizontal, vertical = gaze.horizontal_ratio(), gaze.vertical_ratio()
        if not horizontal:
            horizontal = 0.5
        if not vertical:
            vertical = 0.5
        if horizontal <= 0.4:
            h = 'R'
        elif horizontal < 0.6:
            h = 'C'
        else:
            h = 'L'
        if vertical <= 0.4:
            v = 'U'
        elif vertical < 0.6:
            v = 'C'
        else:
            v = 'D'
        face = cv2.resize(face, (224, 224))
        img_pixels = img_to_array(face)
        img_pixels = np.expand_dims(img_pixels, axis=0)
        img_pixels /= 255

        predictions = emotion_classifier.predict(img_pixels)
        max_index = np.argmax(predictions[0])
        predicted_emotion = EMOTIONS[max_index]
        predicted_emotions[idx] = (predicted_emotion, h, v)

        cv2.putText(anonymized_photo, predicted_emotion, (int(left), int(top)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(anonymized_photo, f"id={idx}", (int(left), int(bottom)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    new_image_name = os.path.join("tmp/emotions", f"{file_id}{extension}")
    cv2.imwrite(new_image_name, anonymized_photo)
    blob = bucket.blob(f"processing/emotions/{file_id}{extension}")
    blob.upload_from_filename(f"tmp/emotions/{file_id}{extension}")
    return predicted_emotions


def analyze_emotions_on_video(filename, file_id, bucket):
    gaze = GazeTracking()
    name, extension = os.path.splitext(filename)
    input_path = f"processing/{file_id}{extension}"
    video = cv2.VideoCapture(input_path)
    name, extension = os.path.splitext(filename)
    anonymized_path = os.path.join("processing/anonymization", f"{id}{extension}")
    anonymized_video = cv2.VideoCapture(anonymized_path)
    timestamps = []
    frames_list = []
    known_encodings = []
    emotions_list = {}
    fps = anonymized_video.get(cv2.CAP_PROP_FPS)
    imageWidth = int(anonymized_video.get(3))
    imageHeight = int(anonymized_video.get(4))

    while video.isOpened():
        ret, frame = video.read()
        anon_ret, anon_frame = anonymized_video.read()

        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        timestamps.append(video.get(cv2.CAP_PROP_POS_MSEC))

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(frame)

        for idx, (top, right, bottom, left) in enumerate(face_locations):
            cv2.rectangle(anon_frame, (left, top), (right, bottom), (255, 255, 255), thickness=4)
            face = gray[top:bottom, left:right]
            face = cv2.resize(face, (224, 224))

            facergb = frame[top:bottom, left:right]
            gaze.refresh(facergb)
            horizontal, vertical = gaze.horizontal_ratio(), gaze.vertical_ratio()
            if not horizontal:
                horizontal = 0.5
            if not vertical:
                vertical = 0.5
            if horizontal <= 0.4:
                h = 'R'
            elif horizontal < 0.6:
                h = 'C'
            else:
                h = 'L'
            if vertical <= 0.4:
                v = 'U'
            elif vertical < 0.6:
                v = 'C'
            else:
                v = 'D'

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
                emotions_list[folder_no].append((predicted_emotion, h, v, timestamps[-1]))
            else:
                emotions_list[folder_no] = [(predicted_emotion, h, v, timestamps[-1])]

            cv2.putText(anon_frame, predicted_emotion, (int(left), int(top)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(anon_frame, f"id={folder_no}", (int(left), int(bottom)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        frames_list.append(anon_frame)
    video.release()
    anonymized_video.release()

    new_video_name = os.path.join("processing/emotions", f"{id}_ns{extension}")
    videowriter = cv2.VideoWriter(new_video_name, cv2.VideoWriter_fourcc(*'DIVX'), fps, (imageWidth, imageHeight))

    for i in range(len(frames_list)):
        videowriter.write(frames_list[i])
    videowriter.release()

    clip = VideoFileClip(new_video_name)

    # loading audio file
    audioclip = AudioFileClip(input_path)

    # adding audio to the video clip
    videoclip = clip.set_audio(audioclip)

    # saving video clip
    new_video_sound_name = os.path.join("processing/emotions", f"{id}{extension}")
    videoclip.write_videofile(new_video_sound_name)

    cv2.destroyAllWindows()
    blob = bucket.blob(f"processing/emotions/{file_id}{extension}")
    blob.upload_from_filename(f"tmp/emotions/{file_id}{extension}")

    return emotions_list