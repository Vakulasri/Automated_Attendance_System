#  Automated_Attendance_System

## Overview
This project implements a real-time face recognition attendance system using **Flask**, **OpenCV**, **Face Recognition**, **SQLAlchemy**, and **pyttsx3** for text-to-speech notifications. The system captures live video feed from the webcam, detects faces, and marks attendance for recognized individuals. It also updates exit times when the person is no longer detected.

## Features
- **Real-Time Face Recognition**: Detects and recognizes faces from the live video feed using OpenCV and Face Recognition libraries.
- **Attendance Management**: Marks attendance and stores it in a database. Updates attendance records with detection and exit times.
- **Text-to-Speech Notifications**: Uses pyttsx3 to provide real-time notifications of recognized individuals.
- **Web Interface**: Provides a web interface to display live video feed and attendance records.
- **Database Integration**: Utilizes SQLAlchemy with SQLite to store and manage attendance data.

## Requirements
Ensure that you have the following Python libraries installed:
- **Flask**: For building the web application
- **OpenCV**: For processing video feed and face recognition
- **Face Recognition**: For face detection and recognition
- **SQLAlchemy**: For ORM-based database interaction
- **pyttsx3**: For text-to-speech functionality
- **SQLite**: For local database storage

## Setup Instructions

- **Clone the repository**:
   ```bash
   git clone https://github.com/Vakulasri/Automated_Attendance_System

### To install the required libraries, run:
```bash
pip install flask opencv-python face-recognition sqlalchemy pyttsx3


