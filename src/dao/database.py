"""
Database connection and initialization handler.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

# Create the SQLAlchemy instance
db = SQLAlchemy()

def init_db(app: Flask):
    """Initialize the database with the Flask application."""
    try:
        # Configure the database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pt2612004%40PT@localhost/vocabulary_learning03'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        # Initialize the database with the app
        db.init_app(app)
        
        # Create all tables
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
    except SQLAlchemyError as e:
        print(f"Database initialization error: {str(e)}")
        raise

def get_db():
    """Get the database instance."""
    return db 