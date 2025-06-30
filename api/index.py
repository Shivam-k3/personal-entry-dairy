from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from textblob import TextBlob
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
CORS(app, supports_credentials=True)

# File paths
USERS_FILE = 'users.json'
VERIFICATION_TOKENS_FILE = 'verification_tokens.json'

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': os.environ.get('EMAIL_USER', 'your-email@gmail.com'),
    'sender_password': os.environ.get('EMAIL_PASSWORD', 'your-app-password'),
    'app_name': 'Personal Daily Journal'
}

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return hash_password(password) == hashed_password

def validate_username(username):
    """Validate username format"""
    return len(username) >= 3 and len(username) <= 20 and username.isalnum()

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

def get_current_user():
    """Get current user from session"""
    return session.get('user_id')

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_user_id():
    """Get user ID from session"""
    user_id = get_current_user()
    if not user_id:
        return None
    return user_id

def get_journal_file(user_id):
    """Get journal file path for user"""
    return f'journal_data/{user_id}_entries.json'

def load_entries(user_id):
    """Load journal entries for user"""
    file_path = get_journal_file(user_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_entries(entries, user_id):
    """Save journal entries for user"""
    os.makedirs('journal_data', exist_ok=True)
    file_path = get_journal_file(user_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob"""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'Positive'
        elif polarity < -0.1:
            return 'Negative'
        else:
            return 'Neutral'
    except:
        return 'Neutral'

def get_suggestion(mood):
    """Get suggestion based on mood"""
    suggestions = {
        'Positive': "Great to see you're feeling positive! Keep up the good energy and maybe try something new today.",
        'Negative': "It's okay to have difficult days. Consider talking to a friend, going for a walk, or doing something you enjoy.",
        'Neutral': "A neutral day can be a good time for reflection. Maybe try a new hobby or activity to add some excitement.",
        'Crisis': "If you're in crisis, please reach out for help. Contact a mental health professional or call a crisis hotline."
    }
    return suggestions.get(mood, "Take care of yourself today.")

@app.route('/api/journal', methods=['POST'])
@require_auth
def add_entry():
    """Add a new journal entry"""
    try:
        data = request.get_json()
        entry_text = data.get('entry', '').strip()
        mood = data.get('mood', 'neutral')
        
        if not entry_text:
            return jsonify({'error': 'Entry text is required'}), 400
        
        user_id = get_current_user()
        
        # Analyze sentiment
        sentiment = analyze_sentiment(entry_text)
        
        # Get suggestion
        suggestion = get_suggestion(sentiment)
        
        # Create entry
        entry = {
            'id': len(load_entries(user_id)) + 1,
            'entry': entry_text,
            'mood': sentiment,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'suggestion': suggestion
        }
        
        # Save entry
        entries = load_entries(user_id)
        entries.append(entry)
        save_entries(entries, user_id)
        
        return jsonify({
            'success': True,
            'entry': entry
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/journal', methods=['GET'])
@require_auth
def get_entries():
    """Get all journal entries for user"""
    try:
        user_id = get_current_user()
        entries = load_entries(user_id)
        
        return jsonify({
            'success': True,
            'entries': entries
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Validate inputs
        if not validate_username(username):
            return jsonify({'error': 'Username must be 3-20 characters and alphanumeric'}), 400
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Load existing users
        users = load_users()
        
        # Check if username or email already exists
        if username in users:
            return jsonify({'error': 'Username already exists'}), 400
        
        for user_data in users.values():
            if user_data.get('email') == email:
                return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        users[username] = {
            'username': username,
            'email': email,
            'password': hash_password(password),
            'email_verified': False,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        save_users(users)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please check your email for verification.'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        users = load_users()
        
        if username not in users:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        user = users[username]
        
        if not verify_password(password, user['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Update last login
        users[username]['last_login'] = datetime.now().isoformat()
        save_users(users)
        
        # Set session
        session['user_id'] = username
        
        return jsonify({
            'success': True,
            'user': {
                'username': username,
                'email': user['email'],
                'email_verified': user.get('email_verified', False)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.pop('user_id', None)
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        user_id = get_current_user()
        if not user_id:
            return jsonify({
                'authenticated': False,
                'user': None
            })
        
        users = load_users()
        if user_id not in users:
            session.pop('user_id', None)
            return jsonify({
                'authenticated': False,
                'user': None
            })
        
        return jsonify({
            'authenticated': True,
            'user': {
                'username': user_id,
                'email': users[user_id].get('email', ''),
                'email_verified': users[user_id].get('email_verified', False)
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Serve static files
@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/index.html')
def serve_index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 