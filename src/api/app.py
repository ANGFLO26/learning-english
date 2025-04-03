"""
Main application file with API routes.
"""
from flask import Flask, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import SQLAlchemyError
import os
from sqlalchemy import desc

from ..dao.database import init_db, get_db
from ..dao.models import User, TestResult
from ..management.topic_manager import TopicManager
from ..management.learning_manager import LearningManager
from ..management.progress_manager import ProgressManager
from ..gui.audio_handler import AudioHandler
from ..gui.template_handler import TemplateHandler

# Create Flask app
app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gui', 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gui', 'static')
)

# Configure the app
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key

# Initialize database
try:
    init_db(app)
except Exception as e:
    print(f"Failed to initialize database: {str(e)}")
    raise

# Initialize GUI components
audio_handler = AudioHandler(app)
template_handler = TemplateHandler(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return template_handler.render_with_user('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db = get_db()
    db.session.rollback()
    return template_handler.render_with_user('500.html'), 500

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('topics'))
    return template_handler.render_with_user('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('topics'))

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            if not name or not email or not password:
                flash('All fields are required')
                return redirect(url_for('register'))

            if User.query.filter_by(email=email).first():
                flash('Email already exists')
                return redirect(url_for('register'))

            if len(password) < 8:
                flash('Password must be at least 8 characters long')
                return redirect(url_for('register'))

            new_user = User(name=name, email=email)
            new_user.set_password(password)
            
            db = get_db()
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))

        except SQLAlchemyError as e:
            db = get_db()
            db.session.rollback()
            print(f"Database Error: {str(e)}")
            flash('An error occurred during registration')
            return redirect(url_for('register'))
        except Exception as e:
            print(f"Registration Error: {str(e)}")
            flash('An error occurred during registration')
            return redirect(url_for('register'))

    return template_handler.render_with_user('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('topics'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.name}!')
            return redirect(url_for('topics'))

        flash('Invalid email or password')
    return template_handler.render_with_user('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/topics')
@login_required
def topics():
    try:
        topics = TopicManager.get_all_topics()
        
        # Get user's progress for all topics
        topic_progress = {}
        for topic in topics:
            # Get test results for this topic
            results = TestResult.query.filter_by(
                user_id=current_user.id,
                topic_id=topic.id
            ).order_by(desc(TestResult.last_attempt)).first()
            
            # Get total vocabularies for this topic
            total_vocab = len(TopicManager.get_vocabularies_by_topic(topic.id))
            
            topic_progress[topic.id] = {
                'completed': results.passed if results else False,
                'highest_score': results.score if results else 0,
                'last_attempt': results.last_attempt if results else None,
                'total_vocab': total_vocab,
                'attempts': results.attempts if results else 0
            }
            
        return template_handler.render_with_user('topics.html', 
            topics=topics,
            topic_progress=topic_progress
        )
    except Exception as e:
        print(f"Error loading topics: {str(e)}")
        flash('Error loading topics', 'error')
        return redirect(url_for('index'))

@app.route('/learn/<int:topic_id>')
@login_required
def learn(topic_id):
    try:
        topic = TopicManager.get_topic_by_id(topic_id)
        vocabularies = TopicManager.get_vocabularies_by_topic(topic_id)
        mode = request.args.get('mode', 'vn_to_en')
        return template_handler.render_with_user('learn.html', topic=topic, vocabularies=vocabularies, mode=mode)
    except Exception as e:
        print(f"Error loading learning content: {str(e)}")
        flash('Error loading learning content')
        return redirect(url_for('topics'))

@app.route('/play_audio/<int:vocab_id>/<string:language>')
@login_required
def play_audio(vocab_id, language):
    try:
        vocab = LearningManager.get_vocabulary_by_id(vocab_id)
        text = vocab.meaning if language == 'vn' else vocab.word
        success = audio_handler.speak_text(text, language)
        return jsonify({'success': success})
    except Exception as e:
        print(f"Error playing audio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test/<int:topic_id>', methods=['GET', 'POST'])
@login_required
def test(topic_id):
    try:
        topic = TopicManager.get_topic_by_id(topic_id)
        if request.method == 'POST':
            try:
                data = request.get_json()
                if not data:
                    raise ValueError("No answer data provided")
                
                score = LearningManager.calculate_test_score(data)
                passed = score >= 90
                
                # Save test result and update leaderboard
                test_result = ProgressManager.save_test_result(current_user.id, topic_id, score, passed)
                if test_result:
                    ProgressManager.update_leaderboard(current_user.id, topic_id, score)
                    return jsonify({
                        'score': score,
                        'passed': passed
                    })
                else:
                    raise ValueError("Failed to save test result")
            except Exception as e:
                print(f"Error processing test submission: {str(e)}")
                return jsonify({'error': 'Failed to process test submission'}), 500
        
        tests = LearningManager.get_tests_by_topic(topic_id)
        if not tests:
            flash('No tests available for this topic', 'warning')
            return redirect(url_for('topics'))
            
        return template_handler.render_with_user('test.html', topic=topic, tests=tests)
    except Exception as e:
        print(f"Error in test mode: {str(e)}")
        flash('Error loading test', 'error')
        return redirect(url_for('topics'))

@app.route('/leaderboard')
def leaderboard():
    try:
        # Get all topics for the filter dropdown
        topics = TopicManager.get_all_topics()
        
        # Get topic_id from query parameters
        topic_id = request.args.get('topic_id', type=int)
        
        # Get leaderboard data
        leaderboard_data = ProgressManager.get_leaderboard(topic_id)
        
        # Get topic names for display
        topic_names = {topic.id: topic.name for topic in topics}
        
        # Get statistics if a topic is selected
        statistics = None
        if topic_id:
            statistics = ProgressManager.get_topic_statistics(topic_id)
        
        return template_handler.render_with_user(
            'leaderboard.html', 
            leaderboard=leaderboard_data,
            topics=topics,
            selected_topic_id=topic_id,
            topic_names=topic_names,
            statistics=statistics
        )
    except Exception as e:
        print(f"Error loading leaderboard: {str(e)}")
        flash('Error loading leaderboard', 'error')
        return redirect(url_for('index'))

@app.route('/history')
@login_required
def history():
    try:
        # Get all topics for reference
        topics = TopicManager.get_all_topics()
        topic_names = {topic.id: topic.name for topic in topics}
        
        # Get user progress
        progress = ProgressManager.get_user_progress(current_user.id)
        
        # Group progress by topic
        progress_by_topic = {}
        for result in progress:
            topic_id = result.topic_id
            if topic_id not in progress_by_topic:
                progress_by_topic[topic_id] = []
            progress_by_topic[topic_id].append(result)
        
        # Sort topics by name
        sorted_topics = sorted(topics, key=lambda x: x.name)
        
        return template_handler.render_with_user(
            'history.html', 
            progress=progress,
            progress_by_topic=progress_by_topic,
            topics=sorted_topics,
            topic_names=topic_names
        )
    except Exception as e:
        print(f"Error loading history: {str(e)}")
        flash('Error loading history', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 