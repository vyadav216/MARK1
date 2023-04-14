import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://smart-attendance-3c91c-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "20X01A06":
        {
            "Name": "Vinayak",
            "Branch": "CSM",
            "Starting_year": 2021,
            "Total attendence": 6,
            "Year": 3,
            "Last_attendence_time":"2022-12-11 00:54:34"
         },
    "20X01A55":
        {
            "Name": "Tim Cook",
            "Branch": "CSE",
            "Starting_year": 2018,
            "Total attendence": 88,
            "Year": 4,
            "Last_attendence_time":"2022-12-11 00:54:34"
        },
    "21X01A66":
        {
            "Name": "Stev Jobs",
            "Branch": "CSE",
            "Starting_year": 2000,
            "Total attendence": 87,
            "Year": 4,
            "Last_attendence_time":"2022-12-11 00:54:34"
        },

}
for key,value in data.items():
    ref.child(key).set(value)
print("Done")