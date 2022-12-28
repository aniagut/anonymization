from deep_privacy.build import build_anonymizer
import os
import pathlib
import cv2
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

def anonymize_video(filename, id, bucket, option, greyscale):
    name, extension = os.path.splitext(filename)
    input_path = f"processing/{id}{extension}"
    blob = bucket.blob(input_path)
    blob.download_to_filename(f"tmp/{id}{extension}")
    output_path = f"tmp/anonymization/{id}{extension}"
    anonymizer = build_anonymizer(model_name=option)
    i_path = pathlib.Path(f"tmp/{id}{extension}")
    o_path = pathlib.Path(output_path)

    anonymizer.anonymize_video(i_path, o_path)
    audiofileclip = AudioFileClip(output_path)
    if greyscale:
        video = cv2.VideoCapture(output_path)
        frames_list = []
        frame_width = int(video.get(3))
        frame_height = int(video.get(4))
        size = (frame_width, frame_height)
        fps = video.get(cv2.CAP_PROP_FPS)
        output_path_ns = f"tmp/anonymization/ns-grey-{id}{extension}"
        output_path = f"tmp/anonymization/grey-{id}{extension}"
        while video.isOpened():
            ret, img = video.read()
            if ret == True:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                frames_list.append(gray)
            else:
                break
        video.release()
        result = cv2.VideoWriter(output_path_ns,
                                 -1,
                                 fps, size)
        for frame in frames_list:
            result.write(frame)
        result.release()
        cv2.destroyAllWindows()
        clip = VideoFileClip(output_path_ns)
        videoclip = clip.set_audio(audiofileclip)

        videoclip.write_videofile(output_path)

    blob = bucket.blob(f"processing/anonymization/{id}{extension}")
    blob.upload_from_filename(output_path)


def anonymize_photo(filename, id, bucket, option, greyscale):
    name, extension = os.path.splitext(filename)
    input_path = f"processing/{id}{extension}"
    blob = bucket.blob(input_path)
    blob.download_to_filename(f"tmp/{id}{extension}")
    output_path = f"tmp/anonymization/{id}{extension}"
    anonymizer = build_anonymizer(model_name=option)
    i_path = pathlib.Path(f"tmp/{id}{extension}")
    o_path = pathlib.Path(output_path)
    anonymizer.anonymize_image_paths([i_path], [o_path])
    if greyscale:
        image = cv2.imread(output_path)
        output_path = f"tmp/anonymization/grey-{id}{extension}"
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(output_path, gray)
    blob = bucket.blob(f"processing/anonymization/{id}{extension}")
    blob.upload_from_filename(output_path)