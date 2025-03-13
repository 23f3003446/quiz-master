from app import db
from flask_login import UserMixin
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), unique = True, nullable = False)
    password_hash = db.Column(db.String(255), nullable = False)
    fullname = db.Column(db.String(255), nullable = False)
    qualification = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    description = db.Column(db.Text)

    chapters = db.relationship('Chapter', backref='subject', lazy = True, cascade = 'all, delete-orphan')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    description = db.Column(db.String)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable = False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key = True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable = False)
    date_of_quiz = db.Column(db.DateTime, nullable = False)
    time_duration = db.Column(db.Integer, nullable = False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade = 'all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade='all, delete-orphan', overlap="users_attempted")

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable = False)
    question_statement = db.Column(db.Text, nullable = False)
    option1 = db.Column(db.String(200), nullable = False)
    option2 = db.Column(db.String(200), nullable = False)
    option3 = db.Column(db.String(200), nullable = False)
    option4 = db.Column(db.String(200), nullable = False)
    correct_option = db.Column(db.String, nullable = False)

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key = True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    time_stamp_of_attempt = db.Column(db.DateTime)
    total_scored = db.Column(db.Integer, nullable = False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'quiz_id', name='uq_user_quiz'),
    )

    