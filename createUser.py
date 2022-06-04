from firebase_admin import auth

firebaseConfig = {
    "apiKey": "AIzaSyDmbYcKZHsK-OMn6aQJLpM4J_0N5ZMeM1I",
    "authDomain": "attendance-automation-bf5e4.firebaseapp.com",
    "databaseURL": "https://attendance-automation-bf5e4-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "attendance-automation-bf5e4",
    "storageBucket": "attendance-automation-bf5e4.appspot.com",
    "messagingSenderId": "615078896726",
    "appId": "1:615078896726:web:dc3acc8691f006b0d847f7"
}


# Creating a User here .......
def create_student(email, password, reg):
    uid = reg
    user = auth.create_user(email=email, password=password, uid=uid)
    return user.uid
