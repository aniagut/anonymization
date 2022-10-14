import face_recognition

# known_image = face_recognition.load_image_file("IMG_0230.JPG")
# unknown_image = face_recognition.load_image_file("IMG_E9620.JPG")
#
# ania_encoding = face_recognition.face_encodings(known_image)[0]
# unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
#
# results = face_recognition.compare_faces([ania_encoding], unknown_encoding)
#
# print(results)
#
# face_locations = face_recognition.face_locations(unknown_image)
#
# print(face_locations)

multiple_faces_img = face_recognition.load_image_file("processing/anonymization/img_in/0/IMG_0131.PNG")

faces_location = face_recognition.face_locations(multiple_faces_img)

print(faces_location)

