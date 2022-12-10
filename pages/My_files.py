import os
from io import BytesIO

import streamlit as st
import yaml
import streamlit_authenticator as stauth

st.set_page_config(page_title="My files")

from firebase_admin import db, storage, credentials, initialize_app, _apps

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

if authentication_status:
    priv_ref = db.reference(f"/{username}/files")
    files =priv_ref.get()
    for file_name, file_info in files.items():
        bucket = storage.bucket()
        extension = file_info['extension']
        blob = bucket.blob(f"{file_name}{extension}")
        file_path = os.path.join("processing/anonymization", f"{file_name}{extension}")
        blob.download_to_filename(file_path)
        fh = open(file_path, 'rb')
        buf = BytesIO(fh.read())
        st.image(buf)
        title = file_info['title']
        description = file_info['description']
        emotions = file_info['emotions']
        if title is not None:
            st.write(f"Title: {title}")
        if description is not None:
            st.write(f"Description: {description}")
        if emotions:
            blob_rap = bucket.blob(f"{file_name}{extension}")
            file_path_rap = os.path.join("processing/anonymization", f"report-{file_name}.pdf")
            blob.download_to_filename(file_path_rap)
            fh_rap = open(file_path_rap, 'rb')
            buf_rap = BytesIO(fh_rap.read())
        st.download_button("Download file", fh, os.path.join(file_name, extension))
        if emotions:
            st.download_button("Download analysis", buf_rap, file_path_rap)
else:
    st.warning("You have to be logged in to view this page.")



