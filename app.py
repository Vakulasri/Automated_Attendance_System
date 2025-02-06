from flask import Flask, render_template, Response
from models import db, Attendance
from sqlalchemy import text
import cv2
import face_recognition
import os
from datetime import datetime, timedelta
import pyttsx3
import threading
import queue
import webbrowser
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Setup for SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize pyttsx3 for text-to-speech
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

# Create a queue for text-to-speech
speech_queue = queue.Queue()

# Text-to-speech thread function
def speak():
    while True:
        text = speech_queue.get()
        if text == "STOP":
            break
        engine.say(text)
        engine.runAndWait()

speech_thread = threading.Thread(target=speak, daemon=True)
speech_thread.start()

# Path to images directory
image_path = 'images'
images = []
classNames = []

# Load images and names
try:
    myList = os.listdir(image_path)
    for cl in myList:
        curImg = cv2.imread(f'{image_path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print("Loaded images and names successfully.")
except Exception as e:
    print(f"Error loading images: {e}")

# Function to compute encodings
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)
        if encode:
            encodeList.append(encode[0])
    return encodeList

# Function to mark attendance
def markAttendance(name):
    now = datetime.now()
    dtString = now.strftime('%Y-%m-%d %H:%M:%S')  # Entry time
    detection_time = dtString  # Set detection time as the time of detection

    try:
        with app.app_context():
            # Check if there's already an attendance record for the person
            existing_record = Attendance.query.filter_by(name=name, exit_time=None).first()
            if existing_record:
                print(f"Attendance already marked for {name} at {existing_record.time}")
            else:
                # Add new attendance record with detection time
                attendance_record = Attendance(name=name, time=dtString, detection_time=detection_time)
                db.session.add(attendance_record)
                db.session.commit()
                print(f"Attendance marked for {name} at {dtString}")
    except Exception as e:
        print(f"Error marking attendance: {e}")


# Function to update exit time
def updateExitTime(name):
    try:
        with app.app_context():
            # Only update the exit time if the name is found and no exit time has been set yet
            record = Attendance.query.filter_by(name=name, exit_time=None).first()
            if record:
                record.exit_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db.session.commit()
                print(f"Exit time for {name} updated.")
            else:
                print(f"No exit time found for {name} to update.")
    except Exception as e:
        print(f"Error updating exit time for {name}: {e}")


# Update exit time if the person is no longer detected after a period.
# Update exit time if the person is no longer detected after a period.
def updateExitTimeIfNeeded(name):
    """Update exit time if the person is no longer detected after a period."""
    if name in last_seen:
        last_seen_time = last_seen[name]
        if datetime.now() - last_seen_time > LEAVE_TIMEOUT:
            # Time has passed, update exit time
            updateExitTime(name)
            print(f"{name} left, updating exit time.")
            currently_detected.discard(name)  # Remove from currently detected list
            del last_seen[name]  # Remove from tracked persons


# Function to check exit time for all people in 'currently_detected'
def checkExitForAll():
    """Check if any of the people have left and update their exit time."""
    for name in list(currently_detected):
        if name not in recognized_names:
            updateExitTimeIfNeeded(name)
            currently_detected.remove(name)


# Find encodings for known faces
encodeListKnown = findEncodings(images)

# Initialize webcam
cap = cv2.VideoCapture(0)
recognized_names = set()
currently_detected = set()  # To track people who are currently detected

# Last seen time tracking
LEAVE_TIMEOUT = timedelta(minutes=10)  # Time after which a person is considered to have left
last_seen = {}  # Dictionary to track the last time a person was seen

def updateExitTimeIfNeeded(name):
    """Update exit time if the person is no longer detected after a period."""
    if name in last_seen:
        last_seen_time = last_seen[name]
        if datetime.now() - last_seen_time > LEAVE_TIMEOUT:
            # Time has passed, update exit time
            updateExitTime(name)
            print(f"{name} left, updating exit time.")
            del last_seen[name]  # Remove from tracked persons

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/attendance')
def attendance():
    records = Attendance.query.all()
    return render_template('attendance.html', records=records)

# Streaming video feed
def gen_frames():
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture video frame.")
            break
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        # Track recognized faces
        recognized_this_frame = set()

        # Check for each face in the frame
        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            if len(faceDis) > 0:
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    recognized_this_frame.add(name)  # Track the recognized name

                    if name not in recognized_names:
                        recognized_names.add(name)
                        currently_detected.add(name)
                        speech_queue.put(f"{name} is present")
                        markAttendance(name)

                    # Update last seen time for this person
                    last_seen[name] = datetime.now()

                    # Draw rectangle and name on the face
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        # Check if anyone has left
        for name in list(currently_detected):
            if name not in recognized_this_frame:
                updateExitTimeIfNeeded(name)

        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/attendance_records')
def attendance_records():
    try:
        records = Attendance.query.all()
        return render_template('attendance_record.html', records=records)
    except Exception as e:
        print(f"Error loading attendance records: {e}")
        return "Error loading attendance records", 500

# Function to alter the table
def alter_table():
    try:
        with app.app_context():
            # Run the ALTER TABLE command to add the new column
            db.session.execute(text('ALTER TABLE attendance ADD COLUMN detection_time TEXT'))
            db.session.commit()
            print("detection_time column added to the attendance table.")
    except Exception as e:
        print(f"Error altering the table: {e}")

# Call the alter_table function once (can be run as part of app initialization)
alter_table()

if __name__ == '__main__':
    # Ensure database initialization
    with app.app_context():
        db.drop_all()  # Drops all tables
        db.create_all()

    # Open browser and start app
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=True)