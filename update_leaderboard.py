from src.api.app import app
from src.dao.database import db
from src.dao.models import TestResult, Leaderboard

def update_leaderboard():
    with app.app_context():
        try:
            # Get all test results grouped by user and topic
            results = TestResult.query.all()
            
            # Group results by user_id and topic_id
            user_topic_scores = {}
            for result in results:
                key = (result.user_id, result.topic_id)
                if key not in user_topic_scores or result.score > user_topic_scores[key]:
                    user_topic_scores[key] = result.score
            
            # Create new leaderboard entries
            for (user_id, topic_id), highest_score in user_topic_scores.items():
                leaderboard_entry = Leaderboard(
                    user_id=user_id,
                    topic_id=topic_id,
                    highest_score=highest_score
                )
                db.session.add(leaderboard_entry)
            
            db.session.commit()
            print("Successfully updated leaderboard data!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating leaderboard: {str(e)}")

if __name__ == '__main__':
    update_leaderboard() 