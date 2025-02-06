from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    time = db.Column(db.String(100))  # Entry time
    exit_time = db.Column(db.String(100), nullable=True)  # Exit time
    detection_time = db.Column(db.String(100), nullable=True)  # Detection time

    def __init__(self, name, time, detection_time=None, exit_time=None):
        self.name = name
        self.time = time
        self.detection_time = detection_time
        self.exit_time = exit_time

# Initialize the app and database
# Ensure your app and db are correctly set up
