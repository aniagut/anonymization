# import face_recognition
# known_image = face_recognition.load_image_file("processing/movie - frame at 0m1s.jpg")
# unknown_image1 = face_recognition.load_image_file("processing/anonymization/111.jpg")
# unknown_image2 = face_recognition.load_image_file("processing/anonymization/112.jpg")
# unknown_image3 = face_recognition.load_image_file("processing/anonymization/113.jpg")
#
# biden_encoding = face_recognition.face_encodings(known_image)[0]
# unknown_encoding1 = face_recognition.face_encodings(unknown_image1)[0]
# unknown_encoding2 = face_recognition.face_encodings(unknown_image2)[0]
# unknown_encoding3 = face_recognition.face_encodings(unknown_image3)[0]
#
# results1 = face_recognition.compare_faces([biden_encoding], unknown_encoding1)
# results2 = face_recognition.compare_faces([biden_encoding], unknown_encoding2)
# results3 = face_recognition.compare_faces([biden_encoding], unknown_encoding3)
# print(results1)
# print(results2)
# print(results3)