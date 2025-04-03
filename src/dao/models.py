"""
Database models for the application.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.text('CURRENT_TIMESTAMP'))
    test_results = db.relationship('TestResult', backref='user', lazy=True)
    leaderboard_entries = db.relationship('Leaderboard', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class VocabularyTopic(db.Model):
    __tablename__ = 'vocabulary_topics'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, server_default=db.text('CURRENT_TIMESTAMP'))
    vocabularies = db.relationship('Vocabulary', backref='topic', lazy=True)
    tests = db.relationship('Test', backref='topic', lazy=True)
    leaderboard_entries = db.relationship('Leaderboard', backref='topic', lazy=True)

class Vocabulary(db.Model):
    __tablename__ = 'vocabularies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('vocabulary_topics.id'), nullable=False)
    word = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.String(255), nullable=False)
    phonetic = db.Column(db.String(100), nullable=True)

class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('vocabulary_topics.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    options = db.Column(db.JSON, nullable=False)

class TestResult(db.Model):
    __tablename__ = 'test_results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('vocabulary_topics.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    passed = db.Column(db.Boolean, nullable=False, default=False)
    attempts = db.Column(db.Integer, nullable=True, default=0)
    last_attempt = db.Column(db.DateTime, nullable=True, server_default=db.text('CURRENT_TIMESTAMP'))

class Leaderboard(db.Model):
    __tablename__ = 'leaderboard'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('vocabulary_topics.id'), nullable=False)
    highest_score = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=True, server_default=db.text('CURRENT_TIMESTAMP'), onupdate=db.text('CURRENT_TIMESTAMP'))

class LearningMode(db.Model):
    __tablename__ = 'learning_modes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True) 