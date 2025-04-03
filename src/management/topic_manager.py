"""
Topic management functionality.
"""
from ..dao.models import VocabularyTopic, Vocabulary
from ..dao.database import get_db

class TopicManager:
    @staticmethod
    def get_all_topics():
        """Get all vocabulary topics."""
        return VocabularyTopic.query.all()
    
    @staticmethod
    def get_topic_by_id(topic_id):
        """Get a specific topic by ID."""
        return VocabularyTopic.query.get_or_404(topic_id)
    
    @staticmethod
    def get_vocabularies_by_topic(topic_id):
        """Get all vocabularies for a specific topic."""
        return Vocabulary.query.filter_by(topic_id=topic_id).all()
    
    @staticmethod
    def create_topic(name, description=None):
        """Create a new topic."""
        topic = VocabularyTopic(name=name, description=description)
        db = get_db()
        db.session.add(topic)
        db.session.commit()
        return topic
    
    @staticmethod
    def add_vocabulary_to_topic(topic_id, word, meaning, phonetic=None):
        """Add a new vocabulary to a topic."""
        vocab = Vocabulary(
            topic_id=topic_id,
            word=word,
            meaning=meaning,
            phonetic=phonetic
        )
        db = get_db()
        db.session.add(vocab)
        db.session.commit()
        return vocab 