# from deep_privacy.build import build_anonymizer
# import os
# import pathlib
# from keras.models import load_model
#
#
# from NEW_emotions_analyzer import analyze_emotions_on_photo
# emotion_model_path = 'best_model.h5'
#
# emotion_classifier = load_model(emotion_model_path, compile=False)
# EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised",
#             "neutral"]
#
# def anonymize_photo(filename, id):
#     path = os.path.join("processing", filename)
#     name, extension = os.path.splitext(filename)
#     output_path = os.path.join("processing/anonymization", f"{id}{extension}")
#     i_path = pathlib.Path(path)
#     o_path = pathlib.Path(output_path)
#     anonymizer = build_anonymizer(model_name="fdf128_retinanet256")
#     anonymizer.anonymize_image_paths([i_path], [o_path])
#
# print(analyze_emotions_on_photo("movie - frame at 0m1s.jpg", "111"))