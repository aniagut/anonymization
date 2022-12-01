from io import BytesIO

import streamlit as st
import os

from firebase_admin import db, storage, credentials, initialize_app, _apps

st.set_page_config(page_title="Public files")

if not _apps:

    cred_obj = credentials.Certificate("emotions-detection-database-firebase-adminsdk-bz9g5-354f63cd0e.json")
    default_app = initialize_app(cred_obj, {
        'databaseURL': "https://emotions-detection-database-default-rtdb.firebaseio.com/",
        'storageBucket': "emotions-detection-database.appspot.com"
    })

pub_ref =db.reference("/public")
files = pub_ref.get()

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
