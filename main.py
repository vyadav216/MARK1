import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL':"https://smart-attendance-3c91c-default-rtdb.firebaseio.com/",
    'storageBucket':"smart-attendance-3c91c.appspot.com"})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread('Resources/background.png')

#Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
#print(len(imgModeList))

# Load the encoding file
print("Loading Encode File....")

file = open('EncodeFile.p','rb')
encodeListknownWithIds = pickle.load(file)
file.close()
encodeListknown, studentIds = encodeListknownWithIds
#print(studentIds)
print("Encodefile Loaded...")

modeType = 0
counter = 0
id = -1
imgStudent = []
   #id = studentIds[matchIndex]
while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[168:168 + 480, 60:60 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListknown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListknown, encodeFace)
            #print("matches", matches)
            #print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            #print("Match Index",matchIndex)

            if matches[matchIndex]:
                #print("known Face Detected")
                #print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                #print(id)


                if counter == 0:
                    cvzone.putTextRect(imgBackground, 'Loading', (275, 400))
                    cv2.imshow('Face Attendence', imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # Get the Image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                # update data of attendence
                datetimeObject = datetime.strptime(studentInfo['Last_attendence_time'],
                                                       "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)


                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['Total attendence']+=1
                    ref.child('Total attendence').set(studentInfo['Total attendence'])
                    ref.child('Last_attendence_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            if modeType !=3:
                if 10<counter<20:
                     modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                if counter < 10:
                    cv2.putText(imgBackground, str(studentInfo['Total attendence']), (865, 127),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (225, 255, 225), 1)

                    cv2.putText(imgBackground, str(studentInfo['Branch']), (1000, 525),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (), 1)
                    cv2.putText(imgBackground, str(id), (980, 457),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['Year']), (1025, 630),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['Starting_year']), (1105, 630),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['Name']), (810 + offset, 425),
                                cv2.FONT_HERSHEY_COMPLEX, 0.9, (50, 50, 50), 1)

                    imgBackground[180:180 + 216, 900:900 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

    #cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    if  cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()