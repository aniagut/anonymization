import json
from io import BytesIO

import streamlit as st
import mimetypes
from face_anonymizer import anonymize_video, anonymize_photo
from NEW_emotions_analyzer import analyze_emotions_on_photo, analyze_emotions_on_video
from image_emotion_gender_demo import read_emotions
import os
import plotly.graph_objects as go
import streamlit_authenticator as stauth
import yaml
from firebase_admin import db, storage, credentials, initialize_app, _apps
from streamlit_modal import Modal
import uuid

# setup firebase
if not _apps:

    cred_obj = credentials.Certificate("emotions-detection-database-firebase-adminsdk-bz9g5-354f63cd0e.json")
    default_app = initialize_app(cred_obj, {
        'databaseURL': "https://emotions-detection-database-default-rtdb.firebaseio.com/",
        'storageBucket': "emotions-detection-database.appspot.com"
    })

ref = db.reference("/")
bucket = storage.bucket()

mimetypes.init()

anonymization_ready, analysis_ready = False, False
file_type, file_name = "", ""

WARNING_FILETYPE = "Uploaded file with unsupported type. " \
                   "Please upload file that is either a video or an image."

with open('credentials.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'sidebar')

if authentication_status:
    st.sidebar.write(f'Welcome *{name}*')
    if st.sidebar.button("View files"):
        pass
    if st.sidebar.button("Update user details"):
        try:
            if authenticator.update_user_details(username, 'Update user details', 'sidebar'):
                with open('credentials.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.sidebar.success('Entries updated successfully')
        except Exception as e:
            st.sidebar.error(e)
    if st.sidebar.button("Reset password"):
        try:
            if authenticator.reset_password(username, 'Reset password', 'sidebar'):
                with open('credentials.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.sidebar.success('Password modified successfully')
        except Exception as e:
            st.sidebar.error(e)
    authenticator.logout('Logout', 'sidebar')
elif authentication_status == False:
    st.sidebar.error('Username/password is incorrect')
elif authentication_status == None:
    st.sidebar.warning('Please enter your username and password')

if not authentication_status:
    if st.sidebar.button("Forgot password"):
        try:
            username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password(
                'Forgot password', 'sidebar')
            if username_forgot_pw:
                with open('credentials.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.sidebar.success('New password sent securely')
            elif username_forgot_pw == False:
                st.sidebar.error('Username not found')
        except Exception as e:
            st.sidebar.error(e)
    if st.sidebar.button("Register"):
        try:
            if authenticator.register_user('Register user', 'sidebar', preauthorization=False):
                with open('credentials.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.sidebar.success('User registered successfully')
        except Exception as e:
            st.sidebar.error(e)

st.title("Face anonymization app")

st.subheader('Choose a picture or video to anonymize')

uploaded_file = st.file_uploader("")

if uploaded_file is not None:
    mimestart = mimetypes.guess_type(uploaded_file.name)

    if mimestart != None:
        type = mimestart[0].split('/')[0]
        if type == 'video':
            video_bytes = uploaded_file.getvalue()
            st.video(video_bytes)
        elif type == 'image':
            image_bytes = uploaded_file.getvalue()
            st.image(image_bytes)
        else:
            st.warning(WARNING_FILETYPE)
    else:
        st.warning(WARNING_FILETYPE)

    col1, col2 = st.columns([1, 1])
    if type in ['video', 'image']:

        with open(os.path.join("processing", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        with col1:
            analyze_button = st.button("Analyze emotions")

        with col2:
            anonymize_button = st.button("Anonymize")

        if analyze_button:
            analysis_ready = False
            anonymization_ready = False
            if type == 'video':
                file_type = type
                id = uuid.uuid4()
                name, extension = os.path.splitext(uploaded_file.name)
                file_name = os.path.join("processing/emotions", f"{id}{extension}")
                with open("filename.txt", "w") as filenameFile:
                    filenameFile.seek(0)
                    filenameFile.write(file_name)
                    filenameFile.truncate()
                with st.spinner("Please wait..."):
                    emotions = analyze_emotions_on_video(uploaded_file.name, id)
                    for id, emotions_list in emotions.items():
                        emotions_dict = {}
                        for emotion, timestamp in emotions_list:
                            if emotions_dict.keys().__contains__(emotion):
                                emotions_dict[emotion] += 1
                            else:
                                emotions_dict[emotion] = 1
                    analysis_ready = True

            elif type == 'image':
                file_type = type
                id = uuid.uuid4()
                name, extension = os.path.splitext(uploaded_file.name)
                file_name = os.path.join("processing/emotions", f"{id}{extension}")
                with open("filename.txt", "w") as filenameFile:
                    filenameFile.seek(0)
                    filenameFile.write(file_name)
                    filenameFile.truncate()
                with st.spinner("Please wait..."):
                    emotions = analyze_emotions_on_photo(uploaded_file.name, id)
                    analysis_ready = True

        if anonymize_button:
            analysis_ready = False
            anonymization_ready = False
            if type == 'video':
                file_type = type
                id = uuid.uuid4()
                name, extension = os.path.splitext(uploaded_file.name)
                file_name = os.path.join("processing/anonymization", f"{id}{extension}")
                with open("filename.txt", "w") as filenameFile:
                    filenameFile.seek(0)
                    filenameFile.write(file_name)
                    filenameFile.truncate()
                with st.spinner("Please wait..."):
                    anonymize_video(uploaded_file.name, id)
                    anonymization_ready = True

            elif type == 'image':
                file_type = type
                id = uuid.uuid4()
                name, extension = os.path.splitext(uploaded_file.name)
                file_name = os.path.join("processing/anonymization", f"{id}{extension}")
                with open("filename.txt", "w") as filenameFile:
                    filenameFile.seek(0)
                    filenameFile.write(file_name)
                    filenameFile.truncate()
                with st.spinner("Please wait..."):
                    anonymize_photo(uploaded_file.name, id)
                    anonymization_ready = True

        if analysis_ready:
            if emotions:
                if file_type == 'image':
                    st.subheader("Emotions analysis on uploaded image")
                    fh = open(file_name, 'rb')
                    buf = BytesIO(fh.read())
                    st.image(buf)
                    st.download_button("Download", fh, file_name)
                elif file_type == 'video':
                    st.subheader("Emotions analysis on uploaded video")
                    fh = open(file_name, 'rb')
                    buf = BytesIO(fh.read())
                    st.video(buf)
                    st.download_button("Download", fh, file_name)
            else:
                st.warning("No emotions detected on uploaded video!")
        if anonymization_ready:
            if file_type == 'image':
                st.subheader("Anonymization on uploaded image")
                fh = open(file_name, 'rb')
                buf = BytesIO(fh.read())
                st.image(buf)
                st.download_button("Download", fh, file_name)
            elif file_type=='video':
                st.subheader("Anonymization on uploaded video")
                fh = open(file_name, 'rb')
                buf = BytesIO(fh.read())
                st.video(buf)
                st.download_button("Download", fh, file_name)

        modal = Modal("Share file", 1)
        if analysis_ready and emotions or anonymization_ready:
            st.button("Share", on_click=modal.open)
        if modal.is_open():
            with modal.container():
                title = st.text_input("Title")
                description = st.text_area("Description")

                private = st.checkbox("Save in library")
                public = st.checkbox("Share")
                print(file_name)
                if st.button("Share file"):
                    with open("filename.txt", "r") as f:
                        file_name = f.read()
                    fullname, extension = os.path.splitext(file_name)
                    if fullname.__contains__("emotions"):
                        fileid = fullname.replace("processing/emotions\\", "")
                    elif fullname.__contains__("anonymization"):
                        fileid = fullname.replace("processing/anonymization\\", "")
                    priv_ref = db.reference(f"/{username}/files/{fileid}")
                    pub_ref = db.reference(f"/public/{fileid}")
                    content = '{ ' + f'"title": "{title}", "description": "{description}", "extension": "{extension}"' + ' }'
                    json_content = json.loads(content)
                    if private:
                        priv_ref.set(json_content)
                    if public:
                        pub_ref.set(json_content)
                    bucket = storage.bucket()
                    blob = bucket.blob(f"{fileid}{extension}")
                    blob.upload_from_filename(file_name)
                    modal.close()


