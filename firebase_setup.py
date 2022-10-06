import firebase_admin
from firebase_admin import db, storage
import json

def setup_firebase():
    cred_obj = firebase_admin.credentials.Certificate("emotions-detection-database-firebase-adminsdk-bz9g5-354f63cd0e.json")
    default_app = firebase_admin.initialize_app(cred_obj, {
        # 'databaseURL': "https://emotions-detection-database-default-rtdb.firebaseio.com/",
        'storageBucket': "emotions-detection-database.appspot.com"
    })

    # ref = db.reference("/")


    fileName="app.py"
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.download_to_filename("new.py")

setup_firebase()