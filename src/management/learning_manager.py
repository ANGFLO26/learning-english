"""
Learning management functionality.
"""
from ..dao.models import LearningMode, Vocabulary, Test
from ..dao.database import get_db

class LearningManager:
    @staticmethod
    def get_learning_modes():
        """Get all available learning modes."""
        return LearningMode.query.all()
    
    @staticmethod
    def get_vocabulary_by_id(vocab_id):
        """Get a specific vocabulary by ID."""
        return Vocabulary.query.get_or_404(vocab_id)
    
    @staticmethod
    def get_tests_by_topic(topic_id):
        """Get all tests for a specific topic."""
        return Test.query.filter_by(topic_id=topic_id).all()
    
    @staticmethod
    def check_test_answer(test_id, answer):
        """Check if an answer is correct for a test."""
        test = Test.query.get_or_404(test_id)
        return answer == test.correct_answer
    
    @staticmethod
    def calculate_test_score(answers):
        """Calculate the score for a test based on answers."""
        total_questions = len(answers)
        correct_answers = 0
        
        for test_id, answer in answers.items():
            if LearningManager.check_test_answer(test_id, answer):
                correct_answers += 1
        
        return (correct_answers / total_questions) * 100 if total_questions > 0 else 0 