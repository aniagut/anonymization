import streamlit as st
st.set_page_config(page_title="My files")

st.write("Hej")
from firebase_admin import db, storage, credentials, initialize_app, _apps

if not _apps:

    cred_obj = credentials.Certificate("emotions-detection-database-firebase-adminsdk-bz9g5-354f63cd0e.json")
    default_app = initialize_app(cred_obj, {
        'databaseURL': "https://emotions-detection-database-default-rtdb.firebaseio.com/",
        'storageBucket': "emotions-detection-database.appspot.com"
    })

ref = db.reference("/jsmith/files")

print(ref.get())

