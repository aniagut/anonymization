import json
from io import BytesIO

import streamlit as st
import mimetypes
from face_anonymizer import anonymize_video, anonymize_photo
import os
import streamlit_authenticator as stauth
import yaml
from firebase_admin import db, storage, credentials, initialize_app, _apps
from streamlit_modal import Modal
import uuid

st.set_page_config(page_title="Main page")

# setup firebase
if not _apps:
    cred_obj = credentials.Certificate(st.secrets["firebase_cert"])
    default_app = initialize_app(cred_obj, {
        'databaseURL': "https://emotions-detection-database-default-rtdb.firebaseio.com/",
        'storageBucket': "emotions-detection-database.appspot.com"
    })

ref = db.reference("/")
bucket = storage.bucket()

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
st.subheader('Choose a picture or video to anonymize')

uploaded_file = st.file_uploader("")
analyze_emotions = False

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

        file_name = uploaded_file.name
        original_name, extension = os.path.splitext(uploaded_file.name)

        file_id = ""
        with open("fileid.txt", "r") as f:
            file_id = f.read()

        anon_path = os.path.join("processing/anonymization", f"{file_id}{extension}")

        if file_id != "" and os.path.isfile(anon_path) and anon_path.__contains__(f"-{original_name}{extension}"):
            anonymization_ready = True
            emotions_path = os.path.join("processing/emotions", f"{file_id}{extension}")
            if os.path.isfile(emotions_path):
                analysis_ready = True
            else:
                analysis_ready = False
        else:
            anonymization_ready, analysis_ready = False, False
            file_id = f"{uuid.uuid4()}-{original_name}"
            with open("fileid.txt", "w") as fileIdFile:
                fileIdFile.seek(0)
                fileIdFile.write(str(file_id))
                fileIdFile.truncate()

        col1, col2 = st.columns(2)
        if not anonymization_ready:
            with col1:
                analyze_emotions = st.checkbox("Analyze emotions")
            with col2:
                anonymize_button = st.button("Anonymize")

        if not anonymization_ready and anonymize_button:
            if type == 'video':
                with st.spinner("Please wait..."):
                    anonymize_video(uploaded_file.name, file_id)
                    # if analyze_emotions:
                    #     emotions = analyze_emotions_on_video(uploaded_file.name, file_id)
                    #     for person_id, emotions_list in emotions.items():
                    #         emotions_dict = {}
                    #         for emotion, timestamp in emotions_list:
                    #             if emotions_dict.keys().__contains__(emotion):
                    #                 emotions_dict[emotion] += 1
                    #             else:
                    #                 emotions_dict[emotion] = 1
                    #     analysis_ready = True
                    anonymization_ready = True

            elif type == 'image':
                with st.spinner("Please wait..."):
                    anonymize_photo(uploaded_file.name, file_id)
                    # if analyze_emotions:
                    #     emotions = analyze_emotions_on_photo(uploaded_file.name, file_id)
                    #     print(emotions)
                    #     analysis_ready = True
                    anonymization_ready = True

        if anonymization_ready:
            path = os.path.join("processing/anonymization", f"{file_id}{extension}")
            if type == 'image':
                st.subheader("Anonymization on uploaded image")
                fh = open(path, 'rb')
                buf = BytesIO(fh.read())
                st.image(buf)
                st.download_button("Download", fh, path)

            elif type == 'video':
                st.subheader("Anonymization on uploaded video")
                fh = open(path, 'rb')
                buf = BytesIO(fh.read())
                st.video(buf)
                st.download_button("Download", fh, path)

        # if analysis_ready:
        #     path = os.path.join("processing/emotions", f"{file_id}{extension}")
        #     emotions = {0: [('surprised', 'L', 'D', 0.0), ('surprised', 'C', 'C', 0.0), ('surprised', 'C', 'C', 33.333333333333336), ('surprised', 'C', 'C', 66.66666666666667), ('surprised', 'C', 'C', 100.0), ('surprised', 'C', 'C', 133.33333333333334), ('surprised', 'C', 'C', 166.66666666666669), ('surprised', 'C', 'C', 200.0), ('sad', 'C', 'C', 233.33333333333334), ('sad', 'C', 'C', 266.6666666666667), ('sad', 'C', 'C', 300.0), ('sad', 'C', 'C', 333.33333333333337), ('sad', 'C', 'C', 366.6666666666667), ('surprised', 'C', 'C', 400.0), ('surprised', 'C', 'C', 433.33333333333337), ('surprised', 'C', 'C', 466.6666666666667), ('surprised', 'C', 'C', 500.0), ('surprised', 'C', 'C', 533.3333333333334), ('surprised', 'C', 'C', 566.6666666666666), ('sad', 'C', 'C', 600.0), ('sad', 'C', 'C', 633.3333333333334), ('sad', 'C', 'C', 666.6666666666667), ('sad', 'C', 'C', 700.0000000000001), ('surprised', 'C', 'C', 733.3333333333334), ('surprised', 'C', 'C', 766.6666666666667), ('sad', 'C', 'C', 800.0), ('sad', 'C', 'C', 833.3333333333334), ('sad', 'C', 'C', 866.6666666666667), ('surprised', 'C', 'C', 900.0), ('sad', 'C', 'C', 933.3333333333334), ('surprised', 'C', 'C', 966.6666666666666), ('sad', 'C', 'C', 1000.0), ('sad', 'C', 'C', 1033.3333333333335), ('surprised', 'C', 'C', 1033.3333333333335), ('sad', 'C', 'C', 1066.6666666666667), ('sad', 'C', 'C', 1100.0), ('sad', 'C', 'C', 1133.3333333333333), ('sad', 'C', 'C', 1166.6666666666667), ('sad', 'C', 'C', 1200.0), ('sad', 'C', 'C', 1233.3333333333335), ('sad', 'C', 'C', 1266.6666666666667), ('sad', 'C', 'C', 1300.0), ('sad', 'C', 'C', 1333.3333333333335), ('sad', 'C', 'C', 1366.6666666666667), ('sad', 'C', 'C', 1400.0000000000002), ('sad', 'C', 'C', 1433.3333333333333), ('sad', 'C', 'C', 1466.6666666666667), ('sad', 'C', 'C', 1500.0), ('surprised', 'C', 'C', 1533.3333333333335), ('surprised', 'C', 'C', 1566.6666666666667), ('surprised', 'C', 'C', 1600.0), ('surprised', 'C', 'C', 1633.3333333333333), ('surprised', 'C', 'C', 1666.6666666666667), ('sad', 'C', 'C', 1700.0000000000002), ('sad', 'C', 'C', 1733.3333333333335), ('surprised', 'C', 'C', 1766.6666666666667), ('surprised', 'C', 'C', 1800.0), ('surprised', 'C', 'C', 1833.3333333333335), ('surprised', 'C', 'C', 1866.6666666666667), ('sad', 'C', 'C', 1900.0000000000002), ('sad', 'C', 'C', 1933.3333333333333), ('sad', 'C', 'C', 1966.6666666666667), ('sad', 'C', 'C', 2000.0), ('sad', 'C', 'C', 2033.3333333333333), ('sad', 'C', 'C', 2066.666666666667), ('sad', 'C', 'C', 2100.0), ('sad', 'C', 'C', 2133.3333333333335), ('sad', 'C', 'C', 2166.666666666667), ('sad', 'C', 'C', 2200.0), ('sad', 'C', 'C', 2233.3333333333335), ('sad', 'C', 'C', 2266.6666666666665), ('sad', 'C', 'C', 2300.0000000000005), ('sad', 'C', 'C', 2333.3333333333335), ('sad', 'C', 'C', 2366.6666666666665), ('sad', 'C', 'C', 2400.0), ('surprised', 'C', 'C', 2433.3333333333335), ('surprised', 'C', 'C', 2466.666666666667), ('surprised', 'C', 'C', 2500.0), ('surprised', 'C', 'C', 2533.3333333333335), ('surprised', 'C', 'C', 2566.666666666667), ('surprised', 'C', 'C', 2600.0), ('surprised', 'C', 'C', 2633.3333333333335), ('surprised', 'C', 'C', 2666.666666666667), ('surprised', 'C', 'C', 2700.0), ('surprised', 'C', 'C', 2733.3333333333335), ('surprised', 'C', 'C', 2766.6666666666665), ('surprised', 'C', 'C', 2800.0000000000005), ('surprised', 'C', 'C', 2833.3333333333335), ('surprised', 'C', 'C', 2866.6666666666665), ('surprised', 'C', 'C', 2900.0000000000005), ('surprised', 'C', 'C', 2933.3333333333335), ('surprised', 'C', 'C', 2966.666666666667), ('surprised', 'C', 'C', 3000.0), ('surprised', 'C', 'C', 3033.3333333333335), ('surprised', 'C', 'C', 3033.3333333333335), ('surprised', 'C', 'C', 3066.666666666667), ('surprised', 'C', 'C', 3100.0), ('surprised', 'C', 'C', 3133.3333333333335), ('surprised', 'C', 'C', 3166.666666666667), ('surprised', 'C', 'C', 3200.0), ('surprised', 'C', 'C', 3233.3333333333335), ('surprised', 'C', 'C', 3233.3333333333335), ('surprised', 'C', 'C', 3266.6666666666665), ('surprised', 'C', 'C', 3266.6666666666665), ('surprised', 'C', 'C', 3300.0000000000005), ('surprised', 'C', 'C', 3300.0000000000005), ('surprised', 'C', 'C', 3333.3333333333335), ('surprised', 'C', 'C', 3333.3333333333335), ('surprised', 'C', 'C', 3366.6666666666665), ('sad', 'C', 'C', 3366.6666666666665), ('surprised', 'C', 'C', 3400.0000000000005), ('sad', 'C', 'C', 3400.0000000000005), ('surprised', 'C', 'C', 3433.3333333333335), ('sad', 'C', 'C', 3433.3333333333335), ('surprised', 'C', 'C', 3466.666666666667), ('surprised', 'C', 'C', 3466.666666666667), ('surprised', 'C', 'C', 3500.0), ('surprised', 'C', 'C', 3500.0), ('surprised', 'C', 'C', 3533.3333333333335), ('surprised', 'C', 'C', 3533.3333333333335), ('surprised', 'C', 'C', 3566.666666666667), ('surprised', 'C', 'C', 3566.666666666667), ('surprised', 'C', 'C', 3600.0), ('surprised', 'C', 'C', 3600.0), ('surprised', 'C', 'C', 3633.3333333333335), ('surprised', 'C', 'C', 3633.3333333333335), ('surprised', 'C', 'C', 3666.666666666667), ('surprised', 'C', 'C', 3666.666666666667), ('surprised', 'C', 'C', 3700.0), ('surprised', 'C', 'C', 3700.0), ('surprised', 'C', 'C', 3733.3333333333335), ('surprised', 'C', 'C', 3733.3333333333335), ('surprised', 'C', 'C', 3766.666666666667), ('surprised', 'C', 'C', 3800.0000000000005), ('surprised', 'C', 'C', 3833.3333333333335), ('sad', 'C', 'C', 3866.6666666666665), ('sad', 'C', 'C', 3900.0000000000005), ('sad', 'C', 'C', 3933.3333333333335), ('happy', 'C', 'C', 3966.666666666667), ('surprised', 'C', 'C', 4000.0), ('surprised', 'C', 'C', 4133.333333333334), ('surprised', 'C', 'C', 4166.666666666667), ('surprised', 'C', 'C', 4266.666666666667), ('surprised', 'C', 'C', 4300.0), ('surprised', 'C', 'C', 4366.666666666667), ('surprised', 'C', 'C', 4400.0), ('surprised', 'C', 'C', 4433.333333333334), ('surprised', 'C', 'C', 4466.666666666667), ('surprised', 'C', 'C', 10633.333333333334), ('surprised', 'C', 'C', 10700.000000000002), ('surprised', 'C', 'C', 11166.666666666668), ('surprised', 'C', 'C', 14266.666666666668), ('surprised', 'C', 'C', 14366.666666666668), ('surprised', 'C', 'C', 14400.0)], 1: [('scared', 'C', 'C', 0.0),('surprised', 'C', 'C', 33.333333333333336), ('surprised', 'C', 'C', 66.66666666666667), ('surprised', 'C', 'C', 100.0), ('surprised', 'C', 'C', 133.33333333333334), ('surprised', 'C', 'C', 166.66666666666669), ('surprised', 'C', 'C', 200.0), ('surprised', 'C', 'C', 233.33333333333334), ('surprised', 'C', 'C', 266.6666666666667), ('surprised', 'C', 'C', 300.0), ('surprised', 'C', 'C', 333.33333333333337), ('surprised', 'C', 'C', 366.6666666666667), ('surprised', 'C', 'C', 400.0), ('surprised', 'C', 'C', 433.33333333333337), ('surprised', 'C', 'C', 466.6666666666667), ('surprised', 'C', 'C', 500.0), ('surprised', 'C', 'C', 533.3333333333334), ('surprised', 'C', 'C', 566.6666666666666), ('happy', 'C', 'C', 600.0), ('happy', 'C', 'C', 633.3333333333334), ('surprised', 'C', 'C', 666.6666666666667), ('surprised', 'C', 'C', 700.0000000000001), ('happy', 'C', 'C', 733.3333333333334), ('scared', 'C', 'C', 766.6666666666667), ('scared', 'C', 'C', 800.0), ('surprised', 'C', 'C', 833.3333333333334), ('surprised', 'C', 'C', 833.3333333333334), ('surprised', 'C', 'C', 866.6666666666667), ('surprised', 'C', 'C', 900.0), ('surprised', 'C', 'C', 933.3333333333334), ('surprised', 'C', 'C', 966.6666666666666), ('surprised', 'C', 'C', 1000.0), ('surprised', 'C', 'C', 1033.3333333333335), ('surprised', 'C', 'C', 1066.6666666666667), ('surprised', 'C', 'C', 1066.6666666666667), ('surprised', 'C', 'C', 1100.0), ('surprised', 'C', 'C', 1100.0), ('surprised', 'C', 'C', 1133.3333333333333), ('surprised', 'C', 'C', 1166.6666666666667), ('surprised', 'C', 'C', 1166.6666666666667), ('surprised', 'C', 'C', 1266.6666666666667), ('surprised', 'C', 'C', 1300.0), ('surprised', 'C', 'C', 1333.3333333333335), ('surprised', 'C', 'C', 1366.6666666666667), ('surprised', 'C', 'C', 1400.0000000000002), ('surprised', 'C', 'C', 1433.3333333333333), ('surprised', 'C', 'C', 1433.3333333333333), ('surprised', 'C', 'C', 1466.6666666666667), ('surprised', 'C', 'C', 1466.6666666666667), ('surprised', 'C', 'C', 1500.0), ('surprised', 'C', 'C', 1500.0), ('surprised', 'C', 'C', 1533.3333333333335), ('surprised', 'C', 'C', 1533.3333333333335), ('surprised', 'C', 'C', 1566.6666666666667), ('surprised', 'C', 'C', 1566.6666666666667), ('surprised', 'C', 'C', 1600.0), ('surprised', 'C', 'C', 1600.0), ('surprised', 'C', 'C', 1633.3333333333333), ('surprised', 'C', 'C', 1633.3333333333333), ('surprised', 'C', 'C', 1666.6666666666667), ('surprised', 'C', 'C', 1666.6666666666667), ('surprised', 'C', 'C', 1700.0000000000002), ('surprised', 'C', 'C', 1733.3333333333335), ('surprised', 'C', 'C', 1766.6666666666667), ('surprised', 'C', 'C', 1800.0), ('surprised', 'C', 'C', 1833.3333333333335), ('surprised', 'C', 'C', 1866.6666666666667), ('surprised', 'C', 'C', 1900.0000000000002), ('surprised', 'C', 'C', 1900.0000000000002), ('surprised', 'C', 'C', 1933.3333333333333), ('surprised', 'C', 'C', 1966.6666666666667), ('surprised', 'C', 'C', 2000.0), ('surprised', 'C', 'C', 2033.3333333333333), ('surprised', 'C', 'C', 2066.666666666667), ('surprised', 'C', 'C', 2100.0), ('surprised', 'C', 'C', 2133.3333333333335), ('surprised', 'C', 'C', 2166.666666666667), ('surprised', 'C', 'C', 2200.0), ('surprised', 'C', 'C', 2233.3333333333335), ('surprised', 'C', 'C', 2266.6666666666665), ('surprised', 'C', 'C', 2300.0000000000005), ('surprised', 'C', 'C', 2333.3333333333335), ('surprised', 'C', 'C', 2366.6666666666665), ('surprised', 'C', 'C', 2400.0), ('surprised', 'C', 'C', 2433.3333333333335), ('surprised', 'C', 'C', 2466.666666666667), ('surprised', 'C', 'C', 2500.0), ('surprised', 'C', 'C', 2533.3333333333335), ('surprised', 'C', 'C', 2566.666666666667), ('surprised', 'C', 'C', 2600.0), ('surprised', 'C', 'C', 2633.3333333333335), ('surprised', 'C', 'C', 2666.666666666667), ('surprised', 'C', 'C', 2700.0), ('surprised', 'C', 'C', 2733.3333333333335), ('surprised', 'C', 'C', 2766.6666666666665), ('surprised', 'C', 'C', 2800.0000000000005), ('surprised', 'C', 'C', 2833.3333333333335), ('surprised', 'C', 'C', 2866.6666666666665), ('surprised', 'C', 'C', 2900.0000000000005), ('surprised', 'C', 'C', 2933.3333333333335), ('surprised', 'C', 'C', 2966.666666666667), ('surprised', 'C', 'C', 3000.0), ('surprised', 'C', 'C', 3033.3333333333335), ('surprised', 'C', 'C', 3066.666666666667), ('surprised', 'C', 'C', 3066.666666666667), ('surprised', 'C', 'C', 3100.0), ('surprised', 'C', 'C', 3100.0), ('surprised', 'C', 'C', 3133.3333333333335), ('surprised', 'C', 'C', 3133.3333333333335), ('surprised', 'C', 'C', 3166.666666666667), ('surprised', 'C', 'C', 3166.666666666667), ('surprised', 'C', 'C', 3200.0), ('surprised', 'C', 'C', 3200.0), ('surprised', 'C', 'C', 3233.3333333333335), ('surprised', 'C', 'C', 3266.6666666666665), ('surprised', 'C', 'C', 3300.0000000000005), ('surprised', 'C', 'C', 3300.0000000000005), ('surprised', 'C', 'C', 3333.3333333333335), ('surprised', 'C', 'C', 3333.3333333333335), ('surprised', 'C', 'C', 3366.6666666666665), ('surprised', 'C', 'C', 3400.0000000000005), ('surprised', 'C', 'C', 3433.3333333333335), ('surprised', 'C', 'C', 3466.666666666667), ('surprised', 'C', 'C', 3500.0), ('surprised', 'C', 'C', 3533.3333333333335), ('surprised', 'C', 'C', 3566.666666666667), ('surprised', 'C', 'C', 3600.0), ('surprised', 'C', 'C', 3633.3333333333335), ('surprised', 'C', 'C', 3633.3333333333335), ('surprised', 'C', 'C', 3666.666666666667), ('surprised', 'C', 'C', 3666.666666666667), ('surprised', 'C', 'C', 3700.0), ('surprised', 'C', 'C', 3700.0), ('surprised', 'C', 'C', 3733.3333333333335), ('surprised', 'C', 'C', 3733.3333333333335), ('surprised', 'C', 'C', 3766.666666666667), ('surprised', 'C', 'C', 3800.0000000000005), ('surprised', 'C', 'C', 3800.0000000000005), ('surprised', 'C', 'C', 3833.3333333333335), ('surprised', 'C', 'C', 3833.3333333333335), ('surprised', 'C', 'C', 3866.6666666666665), ('surprised', 'C', 'C', 3866.6666666666665), ('surprised', 'C', 'C', 3900.0000000000005), ('surprised', 'C', 'C', 3933.3333333333335), ('surprised', 'C', 'C', 3966.666666666667), ('surprised', 'C', 'C', 3966.666666666667), ('surprised', 'C', 'C', 4000.0), ('surprised', 'C', 'C', 4000.0), ('surprised', 'C', 'C', 4033.333333333333), ('surprised', 'C', 'C', 4033.333333333333), ('surprised', 'C', 'C', 4066.6666666666665), ('surprised', 'C', 'C', 4100.000000000001), ('surprised', 'C', 'C', 4133.333333333334), ('surprised', 'C', 'C', 4166.666666666667), ('surprised', 'C', 'C', 4200.0), ('surprised', 'C', 'C', 4200.0), ('surprised', 'C', 'C', 4233.333333333333), ('surprised', 'C', 'C', 4333.333333333334), ('surprised', 'C', 'C', 4333.333333333334), ('surprised', 'C', 'C', 4500.0), ('surprised', 'C', 'C', 4500.0), ('surprised', 'C', 'C', 4533.333333333333), ('surprised', 'C', 'C', 4533.333333333333), ('surprised', 'C', 'C', 4533.333333333333), ('surprised', 'C', 'C', 4566.666666666667), ('surprised', 'C', 'C', 4600.000000000001), ('happy', 'C', 'C', 4666.666666666667), ('scared', 'C', 'C', 4666.666666666667), ('surprised', 'C', 'C', 4666.666666666667), ('surprised', 'C', 'C', 4700.0), ('surprised', 'C', 'C', 4700.0), ('happy', 'C', 'C', 4733.333333333333), ('surprised', 'C', 'C', 4733.333333333333), ('happy', 'C', 'C', 4766.666666666667), ('surprised', 'C', 'C', 4800.0), ('surprised', 'C', 'C', 4833.333333333334), ('surprised', 'C', 'C', 4866.666666666667), ('surprised', 'C', 'C', 4933.333333333334), ('surprised', 'C', 'C', 5033.333333333333), ('surprised', 'C', 'C', 5066.666666666667), ('surprised', 'C', 'C', 5100.000000000001), ('surprised', 'C', 'C', 5133.333333333334), ('surprised', 'C', 'C', 5166.666666666667), ('surprised', 'C', 'C', 5200.0), ('surprised', 'C', 'C', 5233.333333333333), ('surprised', 'C', 'C', 5266.666666666667), ('surprised', 'C', 'C', 5300.0), ('surprised', 'C', 'C', 5333.333333333334), ('surprised', 'C', 'C', 5366.666666666667), ('surprised', 'C', 'C', 5400.0), ('surprised', 'C', 'C', 5433.333333333334), ('surprised', 'C', 'C', 5466.666666666667), ('surprised', 'C', 'C', 5500.0), ('surprised', 'C', 'C', 5533.333333333333), ('surprised', 'C', 'C', 5733.333333333333), ('surprised', 'C', 'C', 5766.666666666667), ('surprised', 'C', 'C', 5800.000000000001), ('surprised', 'C', 'C', 5833.333333333334), ('surprised', 'C', 'C', 5900.0), ('surprised', 'C', 'C', 5933.333333333334), ('surprised', 'C', 'C', 5966.666666666667), ('surprised', 'C', 'C', 5966.666666666667), ('surprised', 'C', 'C', 5966.666666666667), ('surprised', 'C', 'C', 6000.0), ('surprised', 'C', 'C', 6033.333333333333), ('surprised', 'C', 'C', 6033.333333333333), ('surprised', 'C', 'C', 6066.666666666667), ('surprised', 'C', 'C', 6066.666666666667), ('surprised', 'C', 'C', 6100.000000000001), ('surprised', 'C', 'C', 6133.333333333334), ('surprised', 'C', 'C', 6133.333333333334), ('surprised', 'C', 'C', 6200.0), ('surprised', 'C', 'C', 6233.333333333333), ('surprised', 'C', 'C', 6266.666666666667), ('surprised', 'C', 'C', 6333.333333333334), ('surprised', 'C', 'C', 6366.666666666667), ('surprised', 'C', 'C', 6400.0), ('surprised', 'C', 'C', 6400.0), ('surprised', 'C', 'C', 6433.333333333334), ('surprised', 'C', 'C', 6433.333333333334), ('surprised', 'C', 'C', 6466.666666666667), ('surprised', 'C', 'C', 6466.666666666667), ('surprised', 'C', 'C', 6500.0), ('surprised', 'C', 'C', 6500.0), ('surprised', 'C', 'C', 6533.333333333333), ('surprised', 'C', 'C', 6666.666666666667), ('surprised', 'C', 'C', 6700.0), ('surprised', 'C', 'C', 6833.333333333334), ('surprised', 'C', 'C', 7000.0), ('surprised', 'C', 'C', 7033.333333333334), ('surprised', 'C', 'C', 7033.333333333334), ('surprised', 'C', 'C', 7066.666666666667), ('surprised', 'C', 'C', 7100.000000000001), ('surprised', 'C', 'C', 7133.333333333334), ('surprised', 'C', 'C', 7166.666666666667), ('surprised', 'C', 'C', 7933.333333333334), ('surprised', 'C', 'C', 7966.666666666667), ('surprised', 'C', 'C', 8000.0), ('surprised', 'C', 'C', 8133.333333333333), ('surprised', 'C', 'C', 8233.333333333334), ('surprised', 'C', 'C', 8266.666666666668), ('surprised', 'C', 'C', 8300.0), ('surprised', 'C', 'C', 8333.333333333334), ('surprised', 'C', 'C', 8366.666666666668), ('surprised', 'C', 'C', 8400.0), ('surprised', 'C', 'C', 8433.333333333334), ('surprised', 'C', 'C', 8533.333333333334), ('surprised', 'C', 'C', 8566.666666666666), ('surprised', 'C', 'C', 8600.0), ('surprised', 'C', 'C', 8633.333333333332), ('surprised', 'C', 'C', 8666.666666666668), ('surprised', 'C', 'C', 8700.000000000002), ('sad', 'C', 'C', 8733.333333333334), ('surprised', 'C', 'C', 8733.333333333334), ('sad', 'C', 'C', 8766.666666666668), ('surprised', 'C', 'C', 8766.666666666668), ('sad', 'C', 'C', 8800.0), ('surprised', 'C', 'C', 8800.0), ('sad', 'C', 'C', 8833.333333333334), ('surprised', 'C', 'C', 8833.333333333334), ('sad', 'C', 'C', 8866.666666666668), ('sad', 'C', 'C', 8900.0), ('sad', 'C', 'C', 8933.333333333334), ('sad', 'C', 'C', 8966.666666666666), ('sad', 'C', 'C', 9000.0), ('sad', 'C', 'C', 9033.333333333334), ('sad', 'C', 'C', 9066.666666666666), ('sad', 'C', 'C', 9100.0), ('scared', 'C', 'C', 9133.333333333334), ('sad', 'C', 'C', 9166.666666666668), ('sad', 'C', 'C', 9200.000000000002), ('sad', 'C', 'C', 9233.333333333334), ('sad', 'C', 'C', 9266.666666666668), ('sad', 'C', 'C', 9300.0), ('sad', 'C', 'C', 9333.333333333334), ('sad', 'C', 'C', 9366.666666666668), ('sad', 'C', 'C', 9400.0), ('sad', 'C', 'C', 9433.333333333334), ('sad', 'C', 'C', 9466.666666666666), ('surprised', 'C', 'C', 9466.666666666666), ('sad', 'C', 'C', 9500.0), ('surprised', 'C', 'C', 9500.0), ('surprised', 'C', 'C', 9533.333333333334), ('surprised', 'C', 'C', 9533.333333333334), ('sad', 'C', 'C', 9566.666666666666), ('surprised', 'C', 'C', 9566.666666666666), ('sad', 'C', 'C', 9600.0), ('surprised', 'C', 'C', 9600.0), ('surprised', 'C', 'C', 9633.333333333334), ('surprised', 'C', 'C', 9633.333333333334), ('surprised', 'C', 'C', 9666.666666666668), ('surprised', 'C', 'C', 9666.666666666668), ('surprised', 'C', 'C', 9700.000000000002), ('surprised', 'C', 'C', 9700.000000000002), ('surprised', 'C', 'C', 9733.333333333334), ('surprised', 'C', 'C', 9733.333333333334), ('surprised', 'C', 'C', 9766.666666666668), ('surprised', 'C', 'C', 9766.666666666668), ('surprised', 'C', 'C', 9800.0), ('surprised', 'C', 'C', 9800.0), ('sad', 'C', 'C', 9833.333333333334), ('surprised', 'C', 'C', 9833.333333333334), ('sad', 'C', 'C', 9866.666666666668), ('sad', 'C', 'C', 9900.0), ('surprised', 'C', 'C', 9900.0), ('sad', 'C', 'C', 9933.333333333334), ('sad', 'C', 'C', 9966.666666666666), ('sad', 'C', 'C', 10000.0), ('surprised', 'C', 'C', 10000.0), ('sad', 'C', 'C', 10033.333333333334), ('sad', 'C', 'C', 10066.666666666666), ('sad', 'C', 'C', 10100.0), ('sad', 'C', 'C', 10133.333333333334), ('sad', 'C', 'C', 10166.666666666668), ('surprised', 'C', 'C', 10166.666666666668), ('sad', 'C', 'C', 10200.000000000002), ('surprised', 'C', 'C', 10200.000000000002), ('sad', 'C', 'C', 10233.333333333334), ('sad', 'C', 'C', 10266.666666666668), ('sad', 'C', 'C', 10300.0), ('sad', 'C', 'C', 10333.333333333334), ('sad', 'C', 'C', 10366.666666666668), ('surprised', 'C', 'C', 10400.0), ('sad', 'C', 'C', 10433.333333333334), ('sad', 'C', 'C', 10466.666666666666), ('sad', 'C', 'C', 10500.0), ('sad', 'C', 'C', 10533.333333333334), ('sad', 'C', 'C', 10566.666666666666), ('sad', 'C', 'C', 10600.0), ('sad', 'C', 'C', 10633.333333333334), ('sad', 'C', 'C', 10666.666666666668), ('surprised', 'C', 'C', 10666.666666666668), ('sad', 'C', 'C', 10700.000000000002), ('sad', 'C', 'C', 10733.333333333334), ('sad', 'C', 'C', 10766.666666666668), ('sad', 'C', 'C', 10800.0), ('sad', 'C', 'C', 10833.333333333334), ('surprised', 'C', 'C', 10833.333333333334), ('sad', 'C', 'C', 10866.666666666668), ('surprised', 'C', 'C', 10866.666666666668), ('sad', 'C', 'C', 10900.0), ('surprised', 'C', 'C', 10900.0), ('sad', 'C', 'C', 10933.333333333334), ('surprised', 'C', 'C', 10933.333333333334), ('sad', 'C', 'C', 10966.666666666666), ('surprised', 'C', 'C', 10966.666666666666), ('sad', 'C', 'C', 11000.0), ('sad', 'C', 'C', 11033.333333333334), ('surprised', 'C', 'C', 11033.333333333334), ('sad', 'C', 'C', 11066.666666666666), ('sad', 'C', 'C', 11100.0), ('sad', 'C', 'C', 11133.333333333334), ('sad', 'C', 'C', 11166.666666666668), ('sad', 'C', 'C', 11200.000000000002), ('surprised', 'C', 'C', 11200.000000000002), ('sad', 'C', 'C', 11233.333333333334), ('surprised', 'C', 'C', 11233.333333333334), ('sad', 'C', 'C', 11266.666666666668), ('surprised', 'C', 'C', 11266.666666666668), ('sad', 'C', 'C', 11300.0), ('surprised', 'C', 'C', 11300.0), ('sad', 'C', 'C', 11333.333333333334), ('surprised', 'C', 'C', 11333.333333333334), ('sad', 'C', 'C', 11366.666666666668), ('surprised', 'C', 'C', 11366.666666666668), ('sad', 'C', 'C', 11400.0), ('sad', 'C', 'C', 11433.333333333334), ('sad', 'C', 'C', 11466.666666666666), ('sad', 'C', 'C', 11500.0), ('surprised', 'C', 'C', 11500.0), ('sad', 'C', 'C', 11533.333333333334), ('surprised', 'C', 'C', 11533.333333333334), ('sad', 'C', 'C', 11566.666666666666), ('surprised', 'C', 'C', 11566.666666666666), ('sad', 'C', 'C', 11600.000000000002), ('surprised', 'C', 'C', 11600.000000000002), ('scared', 'C', 'C', 11633.333333333334), ('surprised', 'C', 'C', 11666.666666666668), ('scared', 'C', 'C', 11700.000000000002), ('scared', 'C', 'C', 11733.333333333334), ('scared', 'C', 'C', 11766.666666666668), ('scared', 'C', 'C', 11800.0), ('scared', 'C', 'C', 11833.333333333334), ('scared', 'C', 'C', 11866.666666666668), ('scared', 'C', 'C', 11900.0), ('scared', 'C', 'C', 11933.333333333334), ('scared', 'C', 'C', 11966.666666666666), ('scared', 'C', 'C', 12000.0), ('sad', 'C', 'C', 12033.333333333334), ('sad', 'C', 'C', 12066.666666666666), ('scared', 'C', 'C', 12100.000000000002), ('scared', 'C', 'C', 12133.333333333334), ('scared', 'C', 'C', 12166.666666666668), ('surprised', 'C', 'C', 12200.000000000002), ('surprised', 'C', 'C', 12233.333333333334), ('surprised', 'C', 'C', 12266.666666666668), ('surprised', 'C', 'C', 12300.0), ('scared', 'C', 'C', 12333.333333333334), ('sad', 'C', 'C', 12366.666666666668), ('sad', 'C', 'C', 12400.0), ('sad', 'C', 'C', 12433.333333333334), ('sad', 'C', 'C', 12466.666666666666), ('sad', 'C', 'C', 12500.0), ('sad', 'C', 'C', 12533.333333333334), ('sad', 'C', 'C', 12566.666666666666), ('sad', 'C', 'C', 12600.000000000002), ('sad', 'C', 'C', 12633.333333333334), ('surprised', 'C', 'C', 12666.666666666668), ('sad', 'C', 'C', 12700.000000000002), ('sad', 'C', 'C', 12733.333333333334), ('sad', 'C', 'C', 12766.666666666668), ('scared', 'C', 'C', 12800.0), ('scared', 'C', 'C', 12833.333333333334), ('sad', 'C', 'C', 12866.666666666668), ('sad', 'C', 'C', 12900.0), ('scared', 'C', 'C', 12933.333333333334), ('scared', 'C', 'C', 12966.666666666666), ('scared', 'C', 'C', 13000.0), ('scared', 'C', 'C', 13033.333333333334), ('scared', 'C', 'C', 13066.666666666666), ('scared', 'C', 'C', 13100.000000000002), ('scared', 'C', 'C', 13133.333333333334), ('surprised', 'C', 'C', 13166.666666666668), ('sad', 'C', 'C', 13200.000000000002), ('sad', 'C', 'C', 13233.333333333334), ('sad', 'C', 'C', 13266.666666666668), ('scared', 'C', 'C', 13300.0), ('scared', 'C', 'C', 13333.333333333334), ('scared', 'C', 'C', 13366.666666666668), ('scared', 'C', 'C', 13400.0), ('scared', 'C', 'C', 13433.333333333334), ('surprised', 'C', 'C', 13466.666666666666), ('surprised', 'C', 'C', 13500.0), ('surprised', 'C', 'C', 13533.333333333334), ('surprised', 'C', 'C', 13566.666666666666), ('surprised', 'C', 'C', 13600.000000000002), ('surprised', 'C', 'C', 13633.333333333334), ('sad', 'C', 'C', 13666.666666666668), ('sad', 'C', 'C', 13700.000000000002), ('sad', 'C', 'C', 13733.333333333334), ('sad', 'C', 'C', 13766.666666666668), ('scared', 'C', 'C', 13766.666666666668), ('sad', 'C', 'C', 13800.0), ('scared', 'C', 'C', 13800.0), ('sad', 'C', 'C', 13833.333333333334), ('scared', 'C', 'C', 13833.333333333334), ('angry', 'C', 'C', 13866.666666666668), ('angry', 'C', 'C', 13900.0), ('angry', 'C', 'C', 13933.333333333334), ('angry', 'C', 'C', 14000.0), ('sad', 'C', 'C', 14033.333333333334), ('sad', 'C', 'C', 14066.666666666668), ('surprised', 'C', 'C', 14200.000000000002), ('surprised', 'C', 'C', 14233.333333333334), ('surprised', 'C', 'C', 14333.333333333334), ('scared', 'C', 'C', 14366.666666666668), ('scared', 'C', 'C', 14400.0), ('scared', 'C', 'C', 14433.333333333334), ('scared', 'C', 'C', 14466.666666666666), ('scared', 'C', 'C', 14500.0), ('scared', 'C', 'C', 14533.333333333334), ('scared', 'C', 'C', 14566.666666666668), ('sad', 'C', 'C', 14600.000000000002), ('scared', 'C', 'C', 14633.333333333334), ('scared', 'C', 'C', 14666.666666666668), ('scared', 'C', 'C', 14700.000000000002), ('scared', 'C', 'C', 14733.333333333334), ('scared', 'C', 'C', 14766.666666666668), ('scared', 'C', 'C', 14800.0)], 2: [('surprised', 'C', 'C', 33.333333333333336), ('surprised', 'C', 'C', 66.66666666666667), ('surprised', 'C', 'C', 100.0), ('surprised', 'C', 'C', 133.33333333333334), ('surprised', 'C', 'C', 166.66666666666669), ('surprised', 'C', 'C', 200.0), ('surprised', 'C', 'C', 233.33333333333334), ('surprised', 'C', 'C', 266.6666666666667), ('surprised', 'C', 'C', 300.0), ('surprised', 'C', 'C', 366.6666666666667), ('surprised', 'C', 'C', 933.3333333333334), ('surprised', 'C', 'C', 966.6666666666666), ('surprised', 'C', 'C', 1000.0), ('surprised', 'C', 'C', 1066.6666666666667), ('surprised', 'C', 'C', 1100.0), ('surprised', 'C', 'C', 1133.3333333333333), ('surprised', 'C', 'C', 1166.6666666666667), ('surprised', 'C', 'C', 1200.0), ('surprised', 'C', 'C', 1233.3333333333335), ('surprised', 'C', 'C', 1266.6666666666667), ('surprised', 'C', 'C', 1300.0), ('surprised', 'C', 'C', 1333.3333333333335), ('surprised', 'C', 'C', 1366.6666666666667), ('surprised', 'C', 'C', 1400.0000000000002), ('surprised', 'C', 'C', 1433.3333333333333), ('surprised', 'C', 'C', 1466.6666666666667), ('surprised', 'C', 'C', 1500.0), ('surprised', 'C', 'C', 1533.3333333333335), ('surprised', 'C', 'C', 1566.6666666666667), ('surprised', 'C', 'C', 1600.0), ('surprised', 'C', 'C', 1633.3333333333333), ('surprised', 'C', 'C', 1666.6666666666667), ('surprised', 'C', 'C', 1700.0000000000002), ('surprised', 'C', 'C', 1700.0000000000002), ('surprised', 'C', 'C', 1733.3333333333335), ('surprised', 'C', 'C', 1733.3333333333335), ('sad', 'C', 'C', 1766.6666666666667), ('surprised', 'C', 'C', 1800.0), ('sad', 'C', 'C', 1833.3333333333335), ('surprised', 'C', 'C', 1866.6666666666667), ('surprised', 'C', 'C', 1900.0000000000002), ('sad', 'C', 'C', 1933.3333333333333), ('sad', 'C', 'C', 1966.6666666666667), ('sad', 'C', 'C', 2000.0), ('sad', 'C', 'C', 2033.3333333333333), ('sad', 'C', 'C', 2066.666666666667), ('sad', 'C', 'C', 2100.0), ('sad', 'C', 'C', 2133.3333333333335), ('sad', 'C', 'C', 2166.666666666667), ('surprised', 'C', 'C', 3000.0), ('surprised', 'C', 'C', 3200.0), ('surprised', 'C', 'C', 3766.666666666667), ('surprised', 'C', 'C', 3800.0000000000005), ('surprised', 'C', 'C', 3833.3333333333335), ('surprised', 'C', 'C', 3866.6666666666665), ('surprised', 'C', 'C', 3900.0000000000005), ('surprised', 'C', 'C', 3933.3333333333335), ('scared', 'C', 'C', 8833.333333333334), ('surprised', 'C', 'C', 9033.333333333334), ('surprised', 'C', 'C', 9066.666666666666), ('surprised', 'C', 'C', 9100.0), ('surprised', 'C', 'C', 9833.333333333334), ('surprised', 'C', 'C', 9966.666666666666), ('surprised', 'C', 'C', 10133.333333333334), ('surprised', 'C', 'C', 10233.333333333334), ('surprised', 'C', 'C', 10266.666666666668), ('surprised', 'C', 'C', 10300.0), ('surprised', 'C', 'C', 10333.333333333334), ('surprised', 'C', 'C', 10366.666666666668), ('surprised', 'C', 'C', 10533.333333333334), ('surprised', 'C', 'C', 10566.666666666666), ('surprised', 'C', 'C', 10600.0), ('surprised', 'C', 'C', 11400.0), ('surprised', 'C', 'C', 11433.333333333334), ('surprised', 'C', 'C', 11466.666666666666), ('happy', 'C', 'C', 13466.666666666666), ('surprised', 'C', 'C', 14133.333333333334), ('surprised', 'C', 'C', 14166.666666666668)], 3: [('happy', 'C', 'C', 33.333333333333336), ('happy', 'C', 'C', 66.66666666666667), ('happy', 'C', 'C', 166.66666666666669), ('happy', 'C', 'C', 366.6666666666667), ('surprised', 'C', 'C', 533.3333333333334), ('surprised', 'C', 'C', 566.6666666666666), ('surprised', 'C', 'C', 600.0), ('surprised', 'C', 'C', 633.3333333333334), ('surprised', 'C', 'C', 666.6666666666667), ('surprised', 'C', 'C', 700.0000000000001), ('happy', 'C', 'C', 733.3333333333334), ('happy', 'C', 'C', 766.6666666666667), ('surprised', 'C', 'C', 800.0), ('happy', 'C', 'C', 833.3333333333334), ('surprised', 'C', 'C', 2833.3333333333335), ('surprised', 'C', 'C', 2866.6666666666665), ('happy', 'C', 'C', 2900.0000000000005), ('surprised', 'C', 'C', 3000.0), ('surprised', 'C', 'C', 3033.3333333333335), ('surprised', 'C', 'C', 3166.666666666667), ('happy', 'C', 'C', 3200.0), ('surprised', 'C', 'C', 3233.3333333333335), ('surprised', 'C', 'C', 3266.6666666666665), ('surprised', 'C', 'C', 3300.0000000000005), ('happy', 'C', 'C', 3333.3333333333335), ('surprised', 'C', 'C', 3366.6666666666665), ('surprised', 'C', 'C', 3400.0000000000005), ('surprised', 'C', 'C', 3433.3333333333335), ('surprised', 'C', 'C', 3466.666666666667), ('surprised', 'C', 'C', 3500.0), ('surprised', 'C', 'C', 3533.3333333333335), ('surprised', 'C', 'C', 3566.666666666667), ('surprised', 'C', 'C', 3600.0), ('surprised', 'C', 'C', 3633.3333333333335), ('surprised', 'C', 'C', 3666.666666666667), ('surprised', 'C', 'C', 3733.3333333333335), ('surprised', 'C', 'C', 3766.666666666667), ('surprised', 'C', 'C', 3800.0000000000005), ('surprised', 'C', 'C', 4233.333333333333), ('surprised', 'C', 'C', 4333.333333333334), ('surprised', 'C', 'C', 4366.666666666667), ('surprised', 'C', 'C', 4400.0), ('surprised', 'C', 'C', 4433.333333333334)], 4: [('surprised', 'C', 'C', 1200.0), ('surprised', 'C', 'C', 1233.3333333333335), ('surprised', 'C', 'C', 1333.3333333333335), ('surprised', 'C', 'C', 1366.6666666666667), ('surprised', 'C', 'C', 1400.0000000000002), ('surprised', 'C', 'C', 6333.333333333334)], 5: [('surprised', 'C', 'C', 1300.0), ('surprised', 'C', 'C', 1866.6666666666667), ('surprised', 'C', 'C', 3766.666666666667), ('surprised', 'C', 'C', 4566.666666666667), ('surprised', 'C', 'C', 4600.000000000001), ('surprised', 'C', 'C', 4633.333333333334), ('surprised', 'C', 'C', 4733.333333333333), ('surprised', 'C', 'C', 4766.666666666667), ('surprised', 'C', 'C', 4800.0), ('surprised', 'C', 'C', 5900.0), ('surprised', 'C', 'C', 5933.333333333334), ('surprised', 'C', 'C', 6066.666666666667), ('surprised', 'C', 'C', 6100.000000000001), ('surprised', 'C', 'C', 6133.333333333334), ('surprised', 'C', 'C', 6166.666666666667), ('surprised', 'C', 'C', 6200.0), ('surprised', 'C', 'C', 6300.000000000001), ('surprised', 'C', 'C', 6366.666666666667), ('surprised', 'C', 'C', 6533.333333333333), ('surprised', 'C', 'C', 6533.333333333333), ('surprised', 'C', 'C', 6566.666666666667), ('surprised', 'C', 'C', 6600.000000000001), ('surprised', 'C', 'C', 6633.333333333334), ('surprised', 'C', 'C', 6700.0), ('surprised', 'C', 'C', 6733.333333333333), ('surprised', 'C', 'C', 6766.666666666667), ('surprised', 'C', 'C', 6800.000000000001), ('surprised', 'C', 'C', 6800.000000000001), ('surprised', 'C', 'C', 6833.333333333334), ('surprised', 'C', 'C', 6866.666666666667), ('surprised', 'C', 'C', 6900.0), ('surprised', 'C', 'C', 6933.333333333334), ('surprised', 'C', 'C', 6966.666666666667), ('surprised', 'C', 'C', 7000.0), ('surprised', 'C', 'C', 7066.666666666667), ('surprised', 'C', 'C', 7100.000000000001), ('surprised', 'C', 'C', 7133.333333333334), ('surprised', 'C', 'C', 7166.666666666667), ('surprised', 'C', 'C', 7200.0), ('surprised', 'C', 'C', 7233.333333333333), ('surprised', 'C', 'C', 7266.666666666667), ('surprised', 'C', 'C', 7300.000000000001), ('surprised', 'C', 'C', 7333.333333333334), ('surprised', 'C', 'C', 7366.666666666667), ('surprised', 'C', 'C', 7400.0), ('surprised', 'C', 'C', 7433.333333333334), ('surprised', 'C', 'C', 7466.666666666667), ('surprised', 'C', 'C', 7500.0), ('surprised', 'C', 'C', 7533.333333333334), ('surprised', 'C', 'C', 7566.666666666667), ('surprised', 'C', 'C', 7600.000000000001), ('surprised', 'C', 'C', 7633.333333333334), ('surprised', 'C', 'C', 7666.666666666667), ('surprised', 'C', 'C', 7700.0), ('surprised', 'C', 'C', 7733.333333333333), ('surprised', 'C', 'C', 7766.666666666667), ('surprised', 'C', 'C', 7800.000000000001), ('surprised', 'C', 'C', 7833.333333333334), ('surprised', 'C', 'C', 7866.666666666667), ('scared', 'C', 'C', 14300.0)], 6: [('surprised', 'C', 'C', 3900.0000000000005), ('surprised', 'C', 'C', 4100.000000000001)], 7: [('surprised', 'C', 'C', 4500.0), ('surprised', 'C', 'C', 4633.333333333334), ('surprised', 'C', 'C', 4900.0), ('surprised', 'C', 'C', 4966.666666666667), ('surprised', 'C', 'C', 5000.0), ('surprised', 'C', 'C', 5566.666666666667), ('surprised', 'C', 'C', 5600.000000000001), ('surprised', 'C', 'C', 5633.333333333334), ('surprised', 'C', 'C', 5666.666666666667), ('surprised', 'C', 'C', 5700.0), ('surprised', 'C', 'C', 5866.666666666667), ('surprised', 'C', 'C', 6033.333333333333), ('surprised', 'C', 'C', 6100.000000000001), ('surprised', 'C', 'C', 6166.666666666667), ('surprised', 'C', 'C', 6200.0), ('surprised', 'C', 'C', 6233.333333333333), ('surprised', 'C', 'C', 6266.666666666667), ('surprised', 'C', 'C', 6300.000000000001), ('surprised', 'C', 'C', 6333.333333333334), ('surprised', 'C', 'C', 6366.666666666667), ('surprised', 'C', 'C', 6400.0), ('surprised', 'C', 'C', 6433.333333333334), ('surprised', 'C', 'C', 6466.666666666667), ('surprised', 'C', 'C', 6500.0), ('surprised', 'C', 'C', 6666.666666666667), ('surprised', 'C', 'C', 7900.0), ('surprised', 'C', 'C', 8033.333333333333), ('surprised', 'C', 'C', 8066.666666666666), ('surprised', 'C', 'C', 8100.0), ('surprised', 'C', 'C', 8166.666666666668), ('surprised', 'C', 'C', 8200.000000000002), ('surprised', 'C', 'C', 8466.666666666666), ('surprised', 'C', 'C', 8500.0)], 8: [('surprised', 'C', 'C', 4966.666666666667), ('surprised', 'C', 'C', 9400.0), ('surprised', 'C', 'C', 14433.333333333334)], 9: [('surprised', 'C', 'C', 9866.666666666668), ('surprised', 'C', 'C', 9933.333333333334), ('surprised', 'C', 'C', 10033.333333333334), ('surprised', 'C', 'C', 10066.666666666666), ('surprised', 'C', 'C', 10100.0), ('surprised', 'C', 'C', 10400.0), ('surprised', 'C', 'C', 10433.333333333334), ('surprised', 'C', 'C', 10466.666666666666), ('surprised', 'C', 'C', 10500.0), ('sad', 'C', 'C', 11633.333333333334), ('scared', 'C', 'C', 11666.666666666668), ('sad', 'C', 'C', 11700.000000000002), ('sad', 'C', 'C', 11733.333333333334), ('sad', 'C', 'C', 11766.666666666668), ('sad', 'C', 'C', 11800.0), ('sad', 'C', 'C', 11833.333333333334), ('sad', 'C', 'C', 11866.666666666668), ('sad', 'C', 'C', 11900.0), ('sad', 'C', 'C', 11933.333333333334), ('sad', 'C', 'C', 11966.666666666666), ('sad', 'C', 'C', 12000.0), ('sad', 'C', 'C', 12033.333333333334), ('sad', 'C', 'C', 12066.666666666666), ('sad', 'C', 'C', 12100.000000000002), ('sad', 'C', 'C', 12133.333333333334), ('sad', 'C', 'C', 12166.666666666668), ('sad', 'C', 'C', 12200.000000000002), ('sad', 'C', 'C', 12233.333333333334), ('sad', 'C', 'C', 12266.666666666668), ('sad', 'C', 'C', 12300.0), ('sad', 'C', 'C', 12333.333333333334), ('sad', 'C', 'C', 12366.666666666668), ('sad', 'C', 'C', 12400.0), ('sad', 'C', 'C', 12433.333333333334), ('sad', 'C', 'C', 12466.666666666666), ('sad', 'C', 'C', 12500.0), ('sad', 'C', 'C', 12533.333333333334), ('sad', 'C', 'C', 12566.666666666666), ('sad', 'C', 'C', 12600.000000000002), ('sad', 'C', 'C', 12633.333333333334), ('sad', 'C', 'C', 12666.666666666668), ('sad', 'C', 'C', 12700.000000000002), ('sad', 'C', 'C', 12733.333333333334), ('sad', 'C', 'C', 12766.666666666668), ('sad', 'C', 'C', 12800.0), ('sad', 'C', 'C', 12833.333333333334), ('sad', 'C', 'C', 12866.666666666668), ('sad', 'C', 'C', 12900.0), ('sad', 'C', 'C', 12933.333333333334), ('scared', 'C', 'C', 12966.666666666666), ('sad', 'C', 'C', 13000.0), ('scared', 'C', 'C', 13033.333333333334), ('scared', 'C', 'C', 13066.666666666666), ('scared', 'C', 'C', 13100.000000000002), ('scared', 'C', 'C', 13133.333333333334), ('scared', 'C', 'C', 13166.666666666668), ('scared', 'C', 'C', 13200.000000000002), ('scared', 'C', 'C', 13233.333333333334), ('scared', 'C', 'C', 13266.666666666668), ('scared', 'C', 'C', 13300.0), ('scared', 'C', 'C', 13333.333333333334), ('scared', 'C', 'C', 13366.666666666668), ('scared', 'C', 'C', 13400.0), ('scared', 'C', 'C', 13433.333333333334), ('sad', 'C', 'C', 13500.0), ('sad', 'C', 'C', 13533.333333333334), ('sad', 'C', 'C', 13566.666666666666), ('sad', 'C', 'C', 13600.000000000002), ('sad', 'C', 'C', 13633.333333333334), ('sad', 'C', 'C', 13666.666666666668), ('sad', 'C', 'C', 13700.000000000002), ('sad', 'C', 'C', 13733.333333333334), ('sad', 'C', 'C', 13966.666666666666), ('sad', 'C', 'C', 14100.000000000002)]}
        #     if emotions:
        #         if type == 'image':
        #             st.subheader("Emotions analysis on uploaded image")
        #             fh = open(path, 'rb')
        #             buf = BytesIO(fh.read())
        #             st.image(buf)
        #             st.download_button("Download", fh, file_name)
        #         elif type == 'video':
        #             st.subheader("Emotions analysis on uploaded video")
        #             fh = open(path, 'rb')
        #             buf = BytesIO(fh.read())
        #             st.video(buf)
        #             st.download_button("Download", fh, file_name)
        #             fotki = ['processing/plots/1/0.jpg', 'processing/plots/2/0.jpg', 'processing/plots/3/0.jpg',
        #                      'processing/plots/4/0.jpg', 'processing/plots/1/1.jpg', 'processing/plots/2/1.jpg',
        #                      'processing/plots/3/1.jpg', 'processing/plots/4/1.jpg', 'processing/plots/1/2.jpg',
        #                      'processing/plots/2/2.jpg', 'processing/plots/3/2.jpg', 'processing/plots/4/2.jpg',
        #                      'processing/plots/1/3.jpg', 'processing/plots/2/3.jpg', 'processing/plots/3/3.jpg',
        #                      'processing/plots/4/3.jpg', 'processing/plots/1/4.jpg', 'processing/plots/2/4.jpg',
        #                      'processing/plots/3/4.jpg', 'processing/plots/4/4.jpg', 'processing/plots/1/5.jpg',
        #                      'processing/plots/2/5.jpg', 'processing/plots/3/5.jpg', 'processing/plots/4/5.jpg',
        #                      'processing/plots/1/6.jpg', 'processing/plots/2/6.jpg', 'processing/plots/3/6.jpg',
        #                      'processing/plots/4/6.jpg', 'processing/plots/1/7.jpg', 'processing/plots/2/7.jpg',
        #                      'processing/plots/3/7.jpg', 'processing/plots/4/7.jpg', 'processing/plots/1/8.jpg',
        #                      'processing/plots/2/8.jpg', 'processing/plots/3/8.jpg', 'processing/plots/4/8.jpg',
        #                      'processing/plots/1/9.jpg', 'processing/plots/2/9.jpg', 'processing/plots/3/9.jpg',
        #                      'processing/plots/4/9.jpg']
        #             for fotka in fotki:
        #                 fh = open(fotka, 'rb')
        #                 buf = BytesIO(fh.read())
        #                 st.image(buf)
        #         else:
        #             st.warning("No emotions detected on uploaded video!")

        if anonymization_ready:
            modal = Modal("Share file", 1)
            st.button("Share", on_click=modal.open)
            if modal.is_open():
                with modal.container():
                    title = st.text_input("Title")
                    description = st.text_area("Description")

                    private = st.checkbox("Save in library")
                    public = st.checkbox("Share")

                    if st.button("Share file"):
                        priv_ref = db.reference(f"/{username}/files/{file_id}")
                        pub_ref = db.reference(f"/public/{file_id}")
                        content = '{ ' + f'"title": "{title}", "description": "{description}", "extension": "{extension}", "emotions": {analysis_ready}' + ' }'
                        json_content = json.loads(content)
                        if private:
                            priv_ref.set(json_content)
                        if public:
                            pub_ref.set(json_content)
                        bucket = storage.bucket()
                        blob = bucket.blob(f"{file_id}{extension}")
                        file_path = os.path.join("processing/anonymization", f"{file_id}{extension}")
                        blob.upload_from_filename(file_path)
                        if analysis_ready:
                            blob1 = bucket.blob(f"{file_id}e{extension}")
                            e_path = os.path.join("processing/emotions", f"{file_id}{extension}")
                            blob1.upload_from_filename(e_path)
                        modal.close()
