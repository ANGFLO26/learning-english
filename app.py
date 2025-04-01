from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from gtts import gTTS
from playsound import playsound
import tempfile
from threading import Lock

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pt2612004%40PT@localhost/vocabulary_learning03'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['AUDIO_FOLDER'] = os.path.join(app.root_path, 'static', 'audio')

# Create audio folder if it doesn't exist
if not os.path.exists(app.config['AUDIO_FOLDER']):
    os.makedirs(app.config['AUDIO_FOLDER'])

# Create a lock for thread-safe access to the TTS
tts_lock = Lock()

def speak_text(text, language='en'):
    with tts_lock:
        try:
            # Create a temporary file for the audio
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_filename = temp_file.name
            temp_file.close()

            # Generate speech using gTTS
            tts = gTTS(text=text, lang='en' if language == 'en' else 'vi')
            tts.save(temp_filename)
            
            # Play the audio
            playsound(temp_filename)
            
            # Clean up the temporary file
            os.unlink(temp_filename)
            return True
        except Exception as e:
            print(f"TTS Error: {str(e)}")
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            return False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('topics'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect to topics if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('topics'))

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            # Validate required fields
            if not name or not email or not password:
                flash('All fields are required')
                return redirect(url_for('register'))

            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already exists')
                return redirect(url_for('register'))

            # Validate password length
            if len(password) < 8:
                flash('Password must be at least 8 characters long')
                return redirect(url_for('register'))

            # Create new user
            new_user = User(
                name=name,
                email=email
            )
            new_user.set_password(password)

            # Add to database and commit
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please login.')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                print(f"Database Error: {str(e)}")
                flash('An error occurred during registration')
                return redirect(url_for('register'))

        except Exception as e:
            print(f"Registration Error: {str(e)}")
            flash('An error occurred during registration')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect to topics if user is already logged in
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
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/topics')
@login_required
def topics():
    topics = VocabularyTopic.query.all()
    return render_template('topics.html', topics=topics)

@app.route('/learn/<int:topic_id>')
@login_required
def learn(topic_id):
    topic = VocabularyTopic.query.get_or_404(topic_id)
    vocabularies = Vocabulary.query.filter_by(topic_id=topic_id).all()
    mode = request.args.get('mode', 'vn_to_en')  # Default mode is Vietnamese to English
    return render_template('learn.html', topic=topic, vocabularies=vocabularies, mode=mode)

@app.route('/play_audio/<int:vocab_id>/<string:language>')
@login_required
def play_audio(vocab_id, language):
    vocab = Vocabulary.query.get_or_404(vocab_id)
    text = vocab.meaning if language == 'vn' else vocab.word
    
    success = speak_text(text, language)
    return jsonify({'success': success})

@app.route('/test/<int:topic_id>', methods=['GET', 'POST'])
@login_required
def test(topic_id):
    topic = VocabularyTopic.query.get_or_404(topic_id)
    if request.method == 'POST':
        data = request.get_json()
        score = 0
        total_questions = len(data)
        
        for test_id, answer in data.items():
            test = Test.query.get(test_id)
            if test and answer == test.correct_answer:
                score += 1
        
        score_percentage = (score / total_questions) * 100
        passed = score_percentage >= 90
        
        # Create test result
        test_result = TestResult(
            user_id=current_user.id,
            topic_id=topic_id,
            score=score_percentage,
            passed=passed,
            attempts=1
        )
        db.session.add(test_result)
        
        # Update leaderboard
        leaderboard_entry = Leaderboard.query.filter_by(
            user_id=current_user.id,
            topic_id=topic_id
        ).first()
        
        if not leaderboard_entry or score_percentage > leaderboard_entry.highest_score:
            if not leaderboard_entry:
                leaderboard_entry = Leaderboard(
                    user_id=current_user.id,
                    topic_id=topic_id,
                    highest_score=score_percentage
                )
                db.session.add(leaderboard_entry)
            else:
                leaderboard_entry.highest_score = score_percentage
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'score': score_percentage,
            'passed': passed,
            'redirect_url': url_for('topics')
        })
    
    tests = Test.query.filter_by(topic_id=topic_id).all()
    return render_template('test.html', tests=tests, topic=topic)

@app.route('/leaderboard')
def leaderboard():
    topics = VocabularyTopic.query.all()
    results = Leaderboard.query.join(User).join(VocabularyTopic).order_by(
        VocabularyTopic.name,
        Leaderboard.highest_score.desc()
    ).all()
    return render_template('leaderboard.html', results=results, topics=topics)

@app.route('/history')
@login_required
def history():
    topics = VocabularyTopic.query.all()
    results = TestResult.query.filter_by(user_id=current_user.id).order_by(TestResult.last_attempt.desc()).all()
    return render_template('history.html', results=results, topics=topics)

if __name__ == '__main__':
    app.run(debug=True) 