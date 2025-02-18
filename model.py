from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), nullable = False)
    password = db.Column(db.String(255), nullable = False)

    subjects_created = db.relationship('Subject', backref='admin', lazy=True)
    chapters_created = db.relationship('Chapter', backref='admin', lazy=True)
    quizzes_created = db.relationship('Quiz', backref='admin', lazy=True)
    questions_created = db.relationship('Question', backref='admin', lazy=True)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(255), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    full_name = db.Column(db.String(255), nullable = False)
    qualification = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)

    attempted_quizzes = db.relationship('Quiz', secondary = 'scores', backref = db.backref('users_attempted', lazy = 'dynamic'))
    scores = db.relationship('Score', backref='user', lazy = True)


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key = True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable = False)
    name = db.Column(db.String(255), nullable = False)
    description = db.Column(db.Text)

    chapters = db.relationship('Chapter', backref='subject', lazy = True, cascade = 'all, delete-orphan')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key = True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable = False)
    name = db.Column(db.String(255), nullable = False)
    description = db.Column(db.String)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable = False)

    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key = True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable = False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable = False)
    date_of_quiz = db.Column(db.DateTime, nullable = False)
    time_duration = db.Column(db.Integer, nullable = False)
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    questions = db.relationship('Question', backref='quiz', lazy=True, cascade = 'all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key = True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable = False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable = False)
    question_statement = db.Column(db.Text, nullable = False)
    correct_option = db.Column(db.String, nullable = False)

    options = db.relationship('Option', backref='question', lazy=True, cascade='all, delete-orphan')


class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key = True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable = False)
    option_text = db.Column(db.String(255), nullable = False)
    is_correct = db.Column(db.Boolean, default = False)

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