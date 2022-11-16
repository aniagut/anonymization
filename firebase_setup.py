
from firebase_admin import db, storage, credentials, initialize_app

def setup_firebase():
    cred_obj = credentials.Certificate("emotions-detection-database-firebase-adminsdk-bz9g5-354f63cd0e.json")
    default_app = initialize_app(cred_obj, {
        'databaseURL': "https://emotions-detection-database-default-rtdb.firebaseio.com/",
        'storageBucket': "emotions-detection-database.appspot.com"
    })

    ref = db.reference("/")
    bucket = storage.bucket()


    fileName="trimmed3.mp4"
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.download_to_filename("kopia.mp4")

setup_firebase()