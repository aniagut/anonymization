import json
import threading
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
import smtplib, ssl
from email.message import EmailMessage
from streamlit.runtime.scriptrunner import add_script_run_ctx
import ctypes

st.set_page_config(page_title="Main page")
def anonymize_videofile(name, file_id, bucket, option, greyscale):
    anonymize_video(name, file_id, bucket, option, greyscale)

# setup firebase
if not _apps:
    cred_obj = credentials.Certificate(st.secrets["firebase_cert"])
    default_app = initialize_app(cred_obj, {
        'databaseURL': "https://emotions-detection-database-default-rtdb.firebaseio.com/",
        'storageBucket': "emotions-detection-database.appspot.com"
    })

ref = db.reference("/")
bucket = storage.bucket()

# setup mimetypes
mimetypes.init()

WARNING_FILETYPE = "Uploaded file with unsupported type. " \
                   "Please upload file that is either a video or an image."

# setup credentials
blob = bucket.blob('credentials.yaml')
blob.download_to_filename(f"tmp/credentials.yaml")
with open('tmp/credentials.yaml') as cred_file:
    config = yaml.load(cred_file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

st.session_state.username, st.session_state.authentication_status, st.session_state.username = authenticator.login('Login', 'sidebar')

if st.session_state.authentication_status:
    st.sidebar.write(f'Welcome *{st.session_state.name}*')
elif st.session_state.authentication_status == False:
    st.sidebar.error('Username/password is incorrect')
elif st.session_state.authentication_status == None:
    st.sidebar.warning('Please enter your username and password')
if st.session_state.authentication_status:
    try:
        if authenticator.update_user_details(st.session_state.username, 'Update user details', 'sidebar'):
            with open('tmp/credentials.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            blob = bucket.blob('credentials.yaml')
            blob.upload_from_filename(f"tmp/credentials.yaml")
            st.sidebar.success('Entries updated successfully')
    except Exception as e:
        st.sidebar.error(e)
if st.session_state.authentication_status:
    try:
        if authenticator.reset_password(st.session_state.username, 'Reset password', 'sidebar'):
            with open('tmp/credentials.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            blob = bucket.blob('credentials.yaml')
            blob.upload_from_filename(f"tmp/credentials.yaml")
            st.sidebar.success('Password modified successfully')
    except Exception as e:
        st.sidebar.error(e)
if st.session_state.authentication_status:
    authenticator.logout('Logout', 'sidebar')

if st.session_state.authentication_status == False or st.session_state.authentication_status == None:
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password', 'sidebar')
        if username_forgot_pw:
            with open('tmp/credentials.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            blob = bucket.blob('credentials.yaml')
            blob.upload_from_filename(f"tmp/credentials.yaml")

            em = EmailMessage()
            em['From'] = st.secrets["mail"]["login"]
            em['To'] = email_forgot_password
            em['Subject'] = "Password reset"
            message = f"""Your new password {random_password}"""
            em.set_content(message)
            context = ssl.create_default_context()
            port = 465
            smtp_server = "smtp.gmail.com"
            email = st.secrets["mail"]["login"]
            password = st.secrets["mail"]["password"]

            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(email, password)
                server.sendmail(email, email_forgot_password, em.as_string())

            st.sidebar.success('New password sent securely')

        elif username_forgot_pw == False:
            st.sidebar.error('Username not found')
    except Exception as e:
        st.sidebar.error(e)
if st.session_state.authentication_status == False or st.session_state.authentication_status == None:
    try:
        if authenticator.register_user('Register user', 'sidebar', preauthorization=False):
            with open('tmp/credentials.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            blob = bucket.blob('credentials.yaml')
            blob.upload_from_filename(f"tmp/credentials.yaml")
            st.sidebar.success('User registered successfully')
    except Exception as e:
        st.sidebar.error(e)

st.title("Face anonymization app")
st.subheader('Choose a picture or video to anonymize')

uploaded_file = st.file_uploader("")
analyze_emotions = False
greyscale = False
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

    if type and type in ['video', 'image']:

        file_name = uploaded_file.name
        original_name, extension = os.path.splitext(uploaded_file.name)
        anonymization_ready = False

        if "file" in st.session_state and st.session_state.file == uploaded_file.getvalue():

            anon_path = f"processing/anonymization/{st.session_state.file_id}{extension}"
            blob = bucket.blob(anon_path)
            if blob.exists():
                blob.download_to_filename(f"tmp/anonymization/{st.session_state.file_id}{extension}")
                anonymization_ready = True

        if not anonymization_ready:
            file_id = f"{uuid.uuid4()}-{original_name}"
            blob = bucket.blob(f"processing/{file_id}{extension}")
            blob.upload_from_file(uploaded_file)
            st.session_state.file_id = file_id
            st.session_state.file = uploaded_file.getvalue()

        if not anonymization_ready:
            help_message = "Choose from one of the available models:\n" \
                           "- fdf128_rcnn512 - the best quality but high level of similarity\n" \
                           "- fdf128_retinanet512 - medium quality and lower level of similarity\n" \
                           "- fdf128_retinanet256 - low quality but the lowest level of similarity"
            option = st.selectbox('Choose model', ("fdf128_rcnn512", "fdf128_retinanet512","fdf128_retinanet256"), help=help_message)
            col1, col2 = st.columns(2)

            with col1:
                greyscale = st.checkbox("Apply greyscale")
            with col2:
                anonymize_button = st.button("Anonymize")

        if not anonymization_ready and anonymize_button:

            if "thread" in st.session_state:
                if st.session_state.thread.is_alive():
                    exc = ctypes.py_object(SystemExit)
                    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                        ctypes.c_long(st.session_state.thread.ident), exc)

            if "progress" not in st.session_state:
                st.session_state.progress = 0
            st.session_state.progress = 0

            if type == 'video':
                with st.spinner("Please wait..."):
                    bar = st.progress(0)
                    t = threading.Thread(target=anonymize_videofile, args=(uploaded_file.name, st.session_state.file_id, bucket, option, greyscale,))
                    add_script_run_ctx(t)
                    if not "thread" in st.session_state:
                        st.session_state.thread = t
                    st.session_state.thread = t
                    t.start()
                    while st.session_state.progress != 100:
                        bar.progress(st.session_state.progress)
                    if st.session_state.progress == 100:
                        t.join()
                    anonymization_ready = True
            elif type == 'image':
                with st.spinner("Please wait..."):
                    anonymize_photo(uploaded_file.name, st.session_state.file_id, bucket, option, greyscale)
                    anonymization_ready = True

        if anonymization_ready:
            if greyscale:
                path = os.path.join(f"tmp/anonymization/grey-{st.session_state.file_id}{extension}")
            else:
                path = os.path.join(f"tmp/anonymization/{st.session_state.file_id}{extension}")
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

        if anonymization_ready:
            modal = Modal("Share file", 1)
            def open_modal():
               if st.session_state.authentication_status:
                    modal.open()
            st.button("Share", on_click=open_modal)
            if st.session_state.authentication_status == False or st.session_state.authentication_status == None:
                st.warning("You have to be logged in to share this file")
            if modal.is_open():
                with modal.container():
                    title = st.text_input("Title")
                    description = st.text_area("Description")

                    private = st.checkbox("Save in library")
                    public = st.checkbox("Share")

                    if st.button("Share file"):
                        priv_ref = db.reference(f"/{st.session_state.username}/files/{st.session_state.file_id}")
                        pub_ref = db.reference(f"/public/{st.session_state.file_id}")
                        content = '{ ' + f'"title": "{title}", "description": "{description}", "extension": "{extension}", "emotions": "{False}"' + ' }'
                        json_content = json.loads(content)
                        if private:
                            priv_ref.set(json_content)
                        if public:
                            pub_ref.set(json_content)
                        bucket = storage.bucket()
                        blob = bucket.blob(f"{st.session_state.file_id}{extension}")
                        if greyscale:
                            file_path = os.path.join(f"tmp/anonymization/grey-{st.session_state.file_id}{extension}")
                        else:
                            file_path = os.path.join(f"tmp/anonymization/{st.session_state.file_id}{extension}")
                        blob.upload_from_filename(file_path)
                        modal.close()
                        st.success("File successfully shared")