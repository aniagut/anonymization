from io import BytesIO

import streamlit as st
import mimetypes
from emotions_analyzer import analyze_emotion_on_video, analyze_emotion_on_photo
from face_anonymizer import anonymize_video, anonymize_photo
from NEW_emotions_analyzer import analyze_emotions_on_photo, analyze_emotions_on_video
import os
import plotly.graph_objects as go
import streamlit_authenticator as stauth
import yaml

mimetypes.init()

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

st.subheader('Choose a picture or video that you want to work with')

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
    if type in ['video', 'image']:

        with open(os.path.join("processing", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Analyze emotions"):
            if type == 'video':
                with st.spinner("Please wait..."):
                    emotions = analyze_emotions_on_video(uploaded_file.name)
                    for id, emotions_list in emotions.items():
                        emotions_dict = {}
                        for emotion, timestamp in emotions_list:
                            if emotions_dict.keys().__contains__(emotion):
                                emotions_dict[emotion] += 1
                            else:
                                emotions_dict[emotion] = 1
                        fig = go.Figure(
                            go.Pie(
                                labels=list(emotions_dict.keys()),
                                values=list(emotions_dict.values()),
                                hoverinfo="label+percent",
                                textinfo="value",
                                title=f"{id}"
                            )
                        )
                    name, extension = os.path.splitext(uploaded_file.name)
                    new_video_sound_name = os.path.join("processing/emotions", f"{name}_processed_sound{extension}")
                if emotions:
                    st.subheader("Empotions analysis on uploaded video")
                    fh = open(new_video_sound_name, 'rb')
                    buf = BytesIO(fh.read())
                    st.video(buf)
                    st.download_button("Download", fh, new_video_sound_name)
                    st.plotly_chart(fig)
                else:
                    st.warning("No emotions detected on uploaded video!")

            elif type == 'image':
                with st.spinner("Please wait..."):
                    emotions = analyze_emotions_on_photo(uploaded_file.name)
                    name, extension = os.path.splitext(uploaded_file.name)
                    new_image_name = os.path.join("processing/emotions", f"{name}_processed{extension}")
                if emotions:
                    st.subheader("Empotions analysis on uploaded image")
                    fh = open(new_image_name, 'rb')
                    buf = BytesIO(fh.read())
                    st.download_button("Download", fh, new_image_name)
                    st.image(buf)
                else:
                    st.warning("No emotions detected on uploaded image!")

        if st.button("Anonymize"):
            if type == 'video':
                with st.spinner("Please wait..."):
                    anonymize_video(uploaded_file.name)

                    name, extension = os.path.splitext(uploaded_file.name)
                    new_video_sound_name = os.path.join("processing/anonymization", f"{name}_processed{extension}")

                    st.subheader("Anonymization on uploaded video")
                    fh = open(new_video_sound_name, 'rb')
                    buf = BytesIO(fh.read())
                    st.video(buf)
                    st.download_button("Download", fh, new_video_sound_name)
                    st.plotly_chart(fig)

            elif type == 'image':
                with st.spinner("Please wait..."):
                    anonymize_photo(uploaded_file.name)
                    name, extension = os.path.splitext(uploaded_file.name)
                    new_image_name = os.path.join("processing/anonymization", f"{name}_processed{extension}")

                    st.subheader("Anonymization on uploaded image")
                    fh = open(new_image_name, 'rb')
                    buf = BytesIO(fh.read())
                    st.download_button("Download", fh, new_image_name)
                    st.image(buf)
