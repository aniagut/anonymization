import cv2
import numpy as np
from keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

model = load_model("best_model.h5")
emotions = ('angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral')
face_haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def analyze_emotion_on_video(filename):
    path = os.path.join("processing", filename)
    cap = cv2.VideoCapture(path)
    timestamps = []
    frame_list = []
    emotions_list = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    imageWidth = int(cap.get(3))
    imageHeight = int(cap.get(4))

    while (cap.isOpened()):
        ret, frame = cap.read()

        if not ret:
            break
        timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))

        # conversion of BGR to grayscale is necessary to apply this operation
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces = face_haar_cascade.detectMultiScale(gray, 1.32, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), thickness=4)

            face = gray[y:y + w, x:x + h]
            face = cv2.resize(face, (224, 224))

            img_pixels = image.img_to_array(face)
            img_pixels = np.expand_dims(img_pixels, axis=0)
            img_pixels /= 255

            predictions = model.predict(img_pixels)
            max_index = np.argmax(predictions[0])
            predicted_emotion = emotions[max_index]

            cv2.putText(frame, predicted_emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            emotions_list.append((predicted_emotion, timestamps[-1]))
        frame_list.append(frame)

    cap.release()

    name, extension = os.path.splitext(filename)
    new_video_name = os.path.join("processing/emotions", f"{name}_processed{extension}")
    videowriter = cv2.VideoWriter(new_video_name, cv2.VideoWriter_fourcc(*'DIVX'), fps, (imageWidth, imageHeight))
    for i in range(len(frame_list)):
        videowriter.write(frame_list[i])
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


def analyze_emotion_on_photo(filename):
    path = os.path.join("processing", filename)
    photo = cv2.imread(path)

    gray = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)

    faces = face_haar_cascade.detectMultiScale(gray, 1.32, 5)
    predicted_emotions = []

    for (x, y, w, h) in faces:
        cv2.rectangle(photo, (x, y), (x + w, y + h), (255, 255, 255), thickness=4)

        face = gray[y:y + w, x:x + h]
        face = cv2.resize(face, (224, 224))

        img_pixels = image.img_to_array(face)
        img_pixels = np.expand_dims(img_pixels, axis=0)
        img_pixels /= 255

        predictions = model.predict(img_pixels)
        max_index = np.argmax(predictions[0])
        predicted_emotion = emotions[max_index]
        predicted_emotions.append(predicted_emotion)

        cv2.putText(photo, predicted_emotion, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    name, extension = os.path.splitext(filename)
    new_image_name = os.path.join("processing/emotions", f"{name}_processed{extension}")

    cv2.imwrite(new_image_name, photo)

    return predicted_emotions
