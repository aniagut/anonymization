from io import BytesIO

import streamlit as st
import os
import yaml
import streamlit_authenticator as stauth
import mimetypes
from email.message import EmailMessage
import smtplib, ssl

from firebase_admin import db, storage, credentials, initialize_app, _apps

st.set_page_config(page_title="Public files")

if not _apps:
    cred_obj = credentials.Certificate(st.secrets["firebase_cert"])
    default_app = initialize_app(cred_obj, {
        'databaseURL': "https://emotions-detection-database-default-rtdb.firebaseio.com/",
        'storageBucket': "emotions-detection-database.appspot.com"
    })

with open('credentials.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

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
            with open('credentials.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.sidebar.success('Entries updated successfully')
    except Exception as e:
        st.sidebar.error(e)
if st.session_state.authentication_status:
    try:
        if authenticator.reset_password(st.session_state.username, 'Reset password', 'sidebar'):
            with open('credentials.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.sidebar.success('Password modified successfully')
    except Exception as e:
        st.sidebar.error(e)
if st.session_state.authentication_status:
    authenticator.logout('Logout', 'sidebar')

if st.session_state.authentication_status == False or st.session_state.authentication_status == None:
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password', 'sidebar')
        if username_forgot_pw:
            with open('credentials.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)

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
            with open('credentials.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
            st.sidebar.success('User registered successfully')
    except Exception as e:
        st.sidebar.error(e)

if st.session_state.authentication_status:
    pub_ref =db.reference("/public")
    files = pub_ref.get()

    if files:
        for file_name, file_info in files.items():
            bucket = storage.bucket()
            extension = file_info['extension']
            blob = bucket.blob(f"{file_name}{extension}")
            file_path = os.path.join("tmp/anonymization", f"{file_name}{extension}")
            blob.download_to_filename(file_path)
            fh = open(file_path, 'rb')
            buf = BytesIO(fh.read())
            mimestart = mimetypes.guess_type(f"{file_name}{extension}")

            type = mimestart[0].split('/')[0]
            if type == 'video':
                st.video(buf)
            elif type == 'image':
                st.image(buf)
            title = file_info['title']
            description = file_info['description']
            emotions = file_info['emotions']
            if title is not None:
                st.write(f"Title: {title}")
            if description is not None:
                st.write(f"Description: {description}")
            if emotions == "True":
                blob_rap = bucket.blob(f"report-{file_name}.pdf")
                file_path_rap = f"tmp/report/report-{file_name}.pdf"
                blob_rap.download_to_filename(file_path_rap)
                fh_rap = open(file_path_rap, 'rb')
                buf_rap = BytesIO(fh_rap.read())
            st.download_button("Download file", fh, os.path.join(file_name, extension))
            if emotions == "True":
                st.download_button("Download analysis", buf_rap, f"report-{file_name}.pdf")
    else:
        st.warning("No files to display")
else:
    st.warning("You have to be logged in to view this page.")
