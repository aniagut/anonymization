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
from raport_generator import prepare_data_for_plots, PDF
from NEW_emotions_analyzer import analyze_emotions_on_photo, analyze_emotions_on_video



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

with open('credentials.yaml') as cred_file:
    config = yaml.load(cred_file, Loader=yaml.SafeLoader)

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

if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    if st.sidebar.button("Forgot password"):
        try:
            username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password(
                'Forgot password', 'sidebar')
            if username_forgot_pw:
                with open('credentials.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                blob = bucket.blob("credentials.yaml")
                cred_file_name = "credentials.yaml"
                blob.upload_from_filename(cred_file_name)
                st.sidebar.success('New password sent securely')
            elif username_forgot_pw == False:
                st.sidebar.error('Username not found')
        except Exception as e:
            st.sidebar.error(e)
if st.session_state['authentication_status'] == False or st.session_state['authentication_status'] == None:
    if st.sidebar.button("Register"):
        try:
            if authenticator.register_user('Register user', 'sidebar', preauthorization=False):
                with open('credentials.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                blob = bucket.blob("credentials.yaml")
                cred_file_name = "credentials.yaml"
                blob.upload_from_filename(cred_file_name)
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
        blob = bucket.blob(f"processing/{uploaded_file.name}")
        blob.upload_from_file(uploaded_file)

        with open(os.path.join("processing", uploaded_file.name), "w+") as f:
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
                    if analyze_emotions:
                        emotions = analyze_emotions_on_video(uploaded_file.name, file_id)
                        for person_id, emotions_list in emotions.items():
                            emotions_dict = {}
                            for emotion, timestamp in emotions_list:
                                if emotions_dict.keys().__contains__(emotion):
                                    emotions_dict[emotion] += 1
                                else:
                                    emotions_dict[emotion] = 1
                        analysis_ready = True
                    anonymization_ready = True

            elif type == 'image':
                with st.spinner("Please wait..."):
                    anonymize_photo(uploaded_file.name, file_id)
                    if analyze_emotions:
                        emotions = analyze_emotions_on_photo(uploaded_file.name, file_id)
                        analysis_ready = True
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

        if analysis_ready:
            if emotions:
                path = os.path.join("processing/emotions", f"{file_id}{extension}")
                plots_names = prepare_data_for_plots(emotions)
                pdf = PDF()
                for i in range(0, len(plots_names) - 1, 3):
                    pdf.print_page([plots_names[i], plots_names[i + 1], plots_names[i + 2]])
                if len(plots_names) % 3 == 2:
                    pdf.print_page([plots_names[-2], plots_names[-1]])
                elif len(plots_names) % 3 == 1:
                    pdf.print_page([plots_names[-2], plots_names[-1]])
                pdf.output(f'report-{file_id}.pdf', 'F')

                raport_path = os.path.join(f'report-{file_id}.pdf')
                if type == 'image':
                    st.subheader("Emotions analysis on uploaded image")
                    fh = open(path, 'rb')
                    raport = open(raport_path, 'rb')
                    buf = BytesIO(fh.read())
                    st.image(buf)
                    st.download_button("Download", fh, file_name)
                    st.download_button("Download raport", raport, "report-dc9fde7e-faab-4236-a470-cb137621eb2a.pdf")
                elif type == 'video':
                    st.subheader("Emotions analysis on uploaded video")
                    fh = open(path, 'rb')
                    raport = open(raport_path, 'rb')
                    buf = BytesIO(fh.read())
                    st.video(buf)
                    st.download_button("Download", fh, file_name)
                    st.download_button("Download raport", raport, "report-dc9fde7e-faab-4236-a470-cb137621eb2a.pdf")

                else:
                    st.warning("No emotions detected on uploaded video!")

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
                        content = '{ ' + f'"title": "{title}", "description": "{description}", "extension": "{extension}", "emotions": "{analysis_ready}"' + ' }'
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
