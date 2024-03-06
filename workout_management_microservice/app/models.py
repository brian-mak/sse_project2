from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class SavedList(db.Model):
    __tablename__ = 'SavedLists'
    ListID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.String(255), nullable=False)
    Name = db.Column(db.String(255), nullable=False)
    CreationDate = db.Column(db.DateTime, server_default=db.func.now())

    # Relationship - A saved list can contain multiple workouts
    workouts = db.relationship('SavedListWorkout', backref='saved_list', lazy=True)

class SavedListWorkout(db.Model):
    __tablename__ = 'SavedListWorkouts'
    ListID = db.Column(db.Integer, db.ForeignKey('SavedLists.ListID'), primary_key=True)
    WorkoutID = db.Column(db.String(255), primary_key=True)
    WorkoutName = db.Column(db.String(255), nullable=False)
    Equipment = db.Column(db.String(255), nullable=False)
    TargetMuscleGroup = db.Column(db.String(255), nullable=False)
    SecondaryMuscles = db.Column(db.String(255))
