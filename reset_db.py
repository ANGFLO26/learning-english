from src.api.app import app
from src.dao.database import db
from src.dao.models import Leaderboard

with app.app_context():
    # Drop only the leaderboard table to preserve other data
    Leaderboard.__table__.drop(db.engine, checkfirst=True)
    # Create all tables (this will create the new leaderboard table)
    db.create_all() 