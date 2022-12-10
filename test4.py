# from deep_privacy.build import build_anonymizer
# import os
# import pathlib
# from keras.models import load_model
#
#
# emotion_model_path = 'best_model.h5'
#
# emotion_classifier = load_model(emotion_model_path, compile=False)
# EMOTIONS = ["angry", "disgust", "scared", "happy", "sad", "surprised",
#             "neutral"]
#
# def anonymize_video(filename, id):
#     path = os.path.join("processing", filename)
#     name, extension = os.path.splitext(filename)
#     output_path = os.path.join("processing/anonymization", f"{id}{extension}")
#     anonymizer = build_anonymizer(model_name="fdf128_retinanet512")
#     i_path = pathlib.Path(path)
#     o_path = pathlib.Path(output_path)
#     anonymizer.anonymize_video(i_path, o_path)
#
# anonymize_video("trimmed5.mp4", "456")