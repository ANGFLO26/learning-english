"""
Progress and ranking management functionality.
"""
from ..dao.models import TestResult, Leaderboard, User, VocabularyTopic
from ..dao.database import get_db
from sqlalchemy import desc, func
from datetime import datetime

class ProgressManager:
    @staticmethod
    def save_test_result(user_id, topic_id, score, passed):
        """Save a test result."""
        db = get_db()
        try:
            # Check if there's an existing result for this user and topic
            existing_result = TestResult.query.filter_by(
                user_id=user_id,
                topic_id=topic_id
            ).first()
            
            if existing_result:
                # Update existing result
                existing_result.score = score
                existing_result.passed = passed
                existing_result.attempts += 1
                existing_result.last_attempt = datetime.utcnow()
            else:
                # Create new result
                existing_result = TestResult(
                    user_id=user_id,
                    topic_id=topic_id,
                    score=score,
                    passed=passed,
                    attempts=1,
                    last_attempt=datetime.utcnow()
                )
                db.session.add(existing_result)
            
            db.session.commit()
            return existing_result
        except Exception as e:
            db.session.rollback()
            print(f"Error saving test result: {str(e)}")
            return None
    
    @staticmethod
    def update_leaderboard(user_id, topic_id, score):
        """Update the leaderboard with a new score."""
        db = get_db()
        try:
            leaderboard_entry = Leaderboard.query.filter_by(
                user_id=user_id,
                topic_id=topic_id
            ).first()
            
            if not leaderboard_entry:
                leaderboard_entry = Leaderboard(
                    user_id=user_id,
                    topic_id=topic_id,
                    highest_score=score
                )
                db.session.add(leaderboard_entry)
            elif score > leaderboard_entry.highest_score:
                leaderboard_entry.highest_score = score
            
            db.session.commit()
            return leaderboard_entry
        except Exception as e:
            db.session.rollback()
            print(f"Error updating leaderboard: {str(e)}")
            return None
    
    @staticmethod
    def get_user_progress(user_id):
        """Get all test results for a user, ordered by most recent first."""
        try:
            return TestResult.query.filter_by(user_id=user_id).order_by(
                desc(TestResult.last_attempt)
            ).all()
        except Exception as e:
            print(f"Error getting user progress: {str(e)}")
            return []
    
    @staticmethod
    def get_leaderboard(topic_id=None):
        """Get the leaderboard, optionally filtered by topic."""
        try:
            # Join with User to get user names
            query = Leaderboard.query.join(User).join(VocabularyTopic)
            
            # Apply topic filter if provided
            if topic_id:
                query = query.filter(Leaderboard.topic_id == topic_id)
            
            # Order by highest score descending
            return query.order_by(desc(Leaderboard.highest_score)).all()
        except Exception as e:
            print(f"Error getting leaderboard: {str(e)}")
            return []
    
    @staticmethod
    def get_user_rankings(user_id):
        """Get all leaderboard entries for a user."""
        try:
            return Leaderboard.query.filter_by(user_id=user_id).all()
        except Exception as e:
            print(f"Error getting user rankings: {str(e)}")
            return []
    
    @staticmethod
    def get_topic_statistics(topic_id):
        """Get statistics for a specific topic."""
        try:
            db = get_db()
            # Get average score
            avg_score = db.session.query(func.avg(TestResult.score)).filter_by(
                topic_id=topic_id
            ).scalar() or 0
            
            # Get pass rate
            total_tests = TestResult.query.filter_by(topic_id=topic_id).count()
            passed_tests = TestResult.query.filter_by(
                topic_id=topic_id,
                passed=True
            ).count()
            
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            return {
                'average_score': round(avg_score, 2),
                'pass_rate': round(pass_rate, 2),
                'total_attempts': total_tests
            }
        except Exception as e:
            print(f"Error getting topic statistics: {str(e)}")
            return {
                'average_score': 0,
                'pass_rate': 0,
                'total_attempts': 0
            } 