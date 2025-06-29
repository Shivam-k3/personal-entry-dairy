from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from textblob import TextBlob
from datetime import datetime, timedelta
import json
import os
import hashlib
import secrets
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try to import email config, fallback to default if not available
try:
    from email_config import EMAIL_CONFIG
except ImportError:
    # Default email configuration (will need to be updated)
    EMAIL_CONFIG = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'your-email@gmail.com',  # Change this to your email
        'sender_password': 'your-app-password',  # Change this to your app password
        'app_name': 'Personal Daily Journal'
    }

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Generate a secure secret key
CORS(app, supports_credentials=True)

# Directory to store journal entries for different users
JOURNAL_DIR = 'journal_data'
USERS_FILE = 'users.json'
VERIFICATION_TOKENS_FILE = 'verification_tokens.json'

# Create journal directory if it doesn't exist
if not os.path.exists(JOURNAL_DIR):
    os.makedirs(JOURNAL_DIR)

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
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return salt + hash_obj.hexdigest()

def verify_password(password, hashed_password):
    """Verify password against hash"""
    if len(hashed_password) < 32:  # Invalid hash
        return False
    salt = hashed_password[:32]
    hash_obj = hashlib.sha256((password + salt).encode())
    return salt + hash_obj.hexdigest() == hashed_password

def validate_username(username):
    """Validate username format"""
    if not username or len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters long"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

def get_current_user():
    """Get current logged in user from session"""
    return session.get('user_id')

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        user_id = get_current_user()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_user_id():
    """Get user ID from session (for authenticated users) or device ID (for anonymous)"""
    # First try to get authenticated user
    user_id = get_current_user()
    if user_id:
        return f"user_{user_id}"
    
    # Fallback to device-based identification for anonymous users
    device_id = request.headers.get('X-Device-ID')
    if device_id:
        return f"device_{device_id}"
    
    # Generate a unique ID based on IP and user agent
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    unique_string = f"{ip}_{user_agent}"
    return f"anonymous_{hashlib.md5(unique_string.encode()).hexdigest()[:8]}"

def get_journal_file(user_id):
    """Get journal file path for specific user"""
    return os.path.join(JOURNAL_DIR, f'journal_{user_id}.json')

def load_entries(user_id):
    """Load journal entries from JSON file for specific user"""
    journal_file = get_journal_file(user_id)
    if os.path.exists(journal_file):
        try:
            with open(journal_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def save_entries(entries, user_id):
    """Save journal entries to JSON file for specific user"""
    journal_file = get_journal_file(user_id)
    with open(journal_file, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob with improved thresholds and crisis detection"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    # Check for serious negative thoughts first
    serious_negative_words = [
        'suicide', 'kill myself', 'end my life', 'want to die', 'better off dead',
        'no reason to live', 'give up', 'can\'t take it anymore', 'hopeless',
        'worthless', 'burden', 'everyone would be better off', 'no point'
    ]
    
    text_lower = text.lower()
    for word in serious_negative_words:
        if word in text_lower:
            return 'Crisis'  # Special category for serious thoughts
    
    # More sensitive thresholds for better detection
    if polarity > 0.05:  # Lowered from 0.1
        return 'Positive'
    elif polarity < -0.05:  # Raised from -0.1
        return 'Negative'
    else:
        return 'Neutral'

def get_suggestion(mood):
    """Get personalized suggestion based on mood with crisis support"""
    import random
    
    suggestions = {
        'Crisis': [
            "You are not alone. Please call 988 (Suicide & Crisis Lifeline) right now - they're available 24/7 and want to help.",
            "These feelings are temporary, even if they don't feel that way. Please reach out to a crisis counselor at 988.",
            "You matter and your life has value. Please talk to someone you trust or call 988 for immediate support.",
            "It's okay to ask for help. Please call 988 or text HOME to 741741 for crisis support.",
            "You don't have to face this alone. Professional help is available and can make a huge difference.",
            "Please reach out to someone you trust or call 988. You deserve support and care.",
            "These thoughts are serious and you deserve professional help. Please call 988 immediately.",
            "You are stronger than you think. Please get help - call 988 or go to the nearest emergency room."
        ],
        'Positive': [
            "Keep up the great energy! Your positive mindset is contagious.",
            "Celebrate your wins today! You're doing amazing.",
            "Share your joy with others - happiness multiplies when shared.",
            "Take a moment to appreciate how far you've come.",
            "Your positive attitude will help you overcome any challenges.",
            "Great job maintaining such a positive outlook!",
            "Remember this feeling - you're capable of amazing things.",
            "Your happiness is well-deserved. Keep shining!"
        ],
        'Negative': [
            "It's okay to feel this way. Tomorrow is a new day.",
            "Consider talking to a friend or family member about your feelings.",
            "Try taking a walk or doing something you usually enjoy.",
            "Remember that difficult times are temporary. You're stronger than you think.",
            "Be gentle with yourself today. You're doing the best you can.",
            "Consider writing down what's bothering you - it can help clarify your thoughts.",
            "Sometimes a good cry or a long shower can help reset your mood.",
            "You don't have to face this alone. Reach out to someone you trust."
        ],
        'Neutral': [
            "Take a moment to reflect on what could make your day even better.",
            "Consider trying something new or reaching out to someone you haven't talked to in a while.",
            "Sometimes neutral days are perfect for planning and setting new goals.",
            "Use this calm energy to organize your thoughts and priorities.",
            "A neutral day can be a good opportunity to practice mindfulness.",
            "Consider what small changes might bring more joy to your day.",
            "Use this balanced state to make thoughtful decisions.",
            "Sometimes the best days start neutral and get better as they go."
        ]
    }
    
    return random.choice(suggestions.get(mood, ["Reflect on your day and see what insights you can gain."]))

@app.route('/api/journal', methods=['POST'])
def add_entry():
    """Add a new journal entry"""
    try:
        data = request.get_json()
        entry_text = data.get('entry', '').strip()
        mood = data.get('mood', '').strip()
        
        if not entry_text:
            return jsonify({'error': 'Entry text is required'}), 400
        
        # Use provided mood if present, else analyze sentiment
        if mood:
            mood_label = {
                'happy': 'Positive',
                'smile': 'Positive',
                'neutral': 'Neutral',
                'sad': 'Negative',
                'angry': 'Negative',
            }.get(mood, mood)
        else:
            mood_label = analyze_sentiment(entry_text)
        suggestion = get_suggestion(mood_label)
        
        # Create entry
        entry = {
            'id': int(datetime.now().timestamp() * 1000),  # Unique ID
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'entry': entry_text,
            'mood': mood if mood else mood_label,
            'suggestion': suggestion
        }
        
        # Load existing entries and add new one
        user_id = get_user_id()
        entries = load_entries(user_id)
        entries.insert(0, entry)  # Add to beginning
        
        # Keep only last 50 entries to prevent file from getting too large
        entries = entries[:50]
        
        # Save to file
        save_entries(entries, user_id)
        
        return jsonify({
            'success': True,
            'entry': entry,
            'message': 'Entry added successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/journal', methods=['GET'])
def get_entries():
    """Get all journal entries (or last N entries)"""
    try:
        user_id = get_user_id()
        entries = load_entries(user_id)
        
        # Get limit from query parameter (default 7)
        limit = request.args.get('limit', 7, type=int)
        entries = entries[:limit]
        
        return jsonify({
            'success': True,
            'entries': entries,
            'count': len(entries)
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/journal/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    """Delete a specific journal entry"""
    try:
        user_id = get_user_id()
        entries = load_entries(user_id)
        
        # Find and remove entry
        original_count = len(entries)
        entries = [entry for entry in entries if entry.get('id') != entry_id]
        
        if len(entries) == original_count:
            return jsonify({'error': 'Entry not found'}), 404
        
        save_entries(entries, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Entry deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/user-info', methods=['GET'])
def get_user_info():
    """Get current user/device information"""
    try:
        user_id = get_user_id()
        entries = load_entries(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'total_entries': len(entries),
            'first_entry_date': entries[-1]['date'] if entries else None,
            'last_entry_date': entries[0]['date'] if entries else None
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get journal statistics for current user"""
    try:
        user_id = get_user_id()
        entries = load_entries(user_id)
        
        if not entries:
            return jsonify({
                'success': True,
                'user_id': user_id,
                'stats': {
                    'total_entries': 0,
                    'mood_distribution': {},
                    'average_mood': 'No data'
                }
            })
        
        # Count mood distribution
        mood_counts = {}
        for entry in entries:
            mood = entry.get('mood', 'Unknown')
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
        
        # Calculate average mood
        mood_values = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
        total_mood_value = sum(mood_values.get(entry.get('mood', 'Neutral'), 0) for entry in entries)
        avg_mood_value = total_mood_value / len(entries)
        
        if avg_mood_value > 0.3:
            average_mood = 'Positive'
        elif avg_mood_value < -0.3:
            average_mood = 'Negative'
        else:
            average_mood = 'Neutral'
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'stats': {
                'total_entries': len(entries),
                'mood_distribution': mood_counts,
                'average_mood': average_mood
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/index.html')
def serve_index():
    """Serve the main journal app"""
    return send_from_directory('.', 'index.html')

@app.route('/reset-password.html')
def serve_reset_password():
    """Serve the password reset page"""
    return send_from_directory('.', 'reset-password.html')

@app.route('/')
def home():
    """Serve the main page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Journal API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            code { background: #e9ecef; padding: 2px 5px; border-radius: 3px; font-family: monospace; }
            .feature { background: #d4edda; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745; }
            .warning { background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ffc107; }
            .auth { background: #cce5ff; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📖 Personal Daily Journal API</h1>
            <p>Your journal backend is running successfully!</p>
            
            <div class="feature">
                <h3>🔐 User Authentication System</h3>
                <p>Users can now register accounts and log in to access their personal journal entries from any device. Each user has their own private journal storage.</p>
            </div>
            
            <div class="auth">
                <h3>🔑 Authentication Endpoints</h3>
                <div class="endpoint">
                    <h4>POST /api/auth/register</h4>
                    <p>Register a new user account</p>
                    <code>{"username": "your_username", "password": "your_password"}</code>
                </div>
                <div class="endpoint">
                    <h4>POST /api/auth/login</h4>
                    <p>Login with existing credentials</p>
                    <code>{"username": "your_username", "password": "your_password"}</code>
                </div>
                <div class="endpoint">
                    <h4>POST /api/auth/logout</h4>
                    <p>Logout current user</p>
                </div>
                <div class="endpoint">
                    <h4>GET /api/auth/status</h4>
                    <p>Check authentication status</p>
                </div>
                <div class="endpoint">
                    <h4>POST /api/auth/change-password</h4>
                    <p>Change user password (requires authentication)</p>
                    <code>{"current_password": "old", "new_password": "new"}</code>
                </div>
            </div>
            
            <h2>Journal Endpoints (Require Authentication):</h2>
            
            <div class="endpoint">
                <h3>POST /api/journal</h3>
                <p>Add a new journal entry</p>
                <code>{"entry": "Your journal text here"}</code>
            </div>
            
            <div class="endpoint">
                <h3>GET /api/journal</h3>
                <p>Get all journal entries for the logged-in user</p>
                <code>Optional: ?limit=7</code>
            </div>
            
            <div class="endpoint">
                <h3>DELETE /api/journal/&lt;id&gt;</h3>
                <p>Delete a specific entry</p>
            </div>
            
            <div class="endpoint">
                <h3>GET /api/stats</h3>
                <p>Get journal statistics for the logged-in user</p>
            </div>
            
            <div class="endpoint">
                <h3>GET /api/user-info</h3>
                <p>Get user information and entry summary</p>
            </div>
            
            <div class="warning">
                <h3>⚠️ Important Notes:</h3>
                <ul>
                    <li>All journal endpoints now require user authentication</li>
                    <li>Each user has their own separate journal storage</li>
                    <li>Users can access their entries from any device by logging in</li>
                    <li>Passwords are securely hashed with salt</li>
                    <li>Sessions are maintained using secure cookies</li>
                </ul>
            </div>
            
            <p><a href="/index.html" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Open Journal App</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user (no email verification)"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        
        # Validate input
        if not username or not password or not email:
            return jsonify({'error': 'Username, password, and email are required'}), 400
        
        # Validate username format
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Load existing users
        users = load_users()
        
        # Check if username already exists
        if username in users:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        for user_data in users.values():
            if user_data.get('email') == email:
                return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password and create user (no verification)
        hashed_password = hash_password(password)
        users[username] = {
            'password': hashed_password,
            'email': email,
            'email_verified': True,  # Always true now
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        # Save users
        save_users(users)
        
        # Log in the user immediately
        session['user_id'] = username
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'username': username,
                'email': email,
                'email_verified': True
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/verify-email', methods=['GET'])
def verify_email():
    """Verify email address using token"""
    try:
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'Verification token is required'}), 400
        
        tokens = load_verification_tokens()
        if token not in tokens:
            return jsonify({'error': 'Invalid or expired verification token'}), 400
        
        token_data = tokens[token]
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now() > expires_at:
            del tokens[token]
            save_verification_tokens(tokens)
            return jsonify({'error': 'Verification token has expired'}), 400
        
        # Verify email
        users = load_users()
        username = token_data['username']
        
        if username in users:
            users[username]['email_verified'] = True
            save_users(users)
        
        # Remove used token
        del tokens[token]
        save_verification_tokens(tokens)
        
        return jsonify({
            'success': True,
            'message': 'Email verified successfully! You can now log in to your account.'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Find user by email
        users = load_users()
        username = None
        for uname, user_data in users.items():
            if user_data.get('email') == email:
                username = uname
                break
        
        if not username:
            # Don't reveal if email exists or not for security
            return jsonify({
                'success': True,
                'message': 'If an account with this email exists, a password reset link has been sent.'
            })
        
        # Generate reset token
        token = generate_verification_token()
        tokens = load_verification_tokens()
        tokens[token] = {
            'username': username,
            'email': email,
            'type': 'password_reset',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        save_verification_tokens(tokens)
        
        # Send reset email
        subject, html_content, text_content = create_verification_email(email, token, 'password_reset')
        email_sent = send_email(email, subject, html_content, text_content)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Password reset link has been sent to your email.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send password reset email. Please try again.'
            })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        # Validate password strength
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        tokens = load_verification_tokens()
        if token not in tokens:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        token_data = tokens[token]
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now() > expires_at:
            del tokens[token]
            save_verification_tokens(tokens)
            return jsonify({'error': 'Reset token has expired'}), 400
        
        # Check token type
        if token_data['type'] != 'password_reset':
            return jsonify({'error': 'Invalid token type'}), 400
        
        # Update password
        users = load_users()
        username = token_data['username']
        
        if username in users:
            users[username]['password'] = hash_password(new_password)
            save_users(users)
        
        # Remove used token
        del tokens[token]
        save_verification_tokens(tokens)
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully! You can now log in with your new password.'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Find user by email
        users = load_users()
        username = None
        for uname, user_data in users.items():
            if user_data.get('email') == email:
                username = uname
                break
        
        if not username:
            return jsonify({'error': 'No account found with this email'}), 404
        
        # Check if already verified
        if users[username].get('email_verified', False):
            return jsonify({'error': 'Email is already verified'}), 400
        
        # Generate new verification token
        token = generate_verification_token()
        tokens = load_verification_tokens()
        tokens[token] = {
            'username': username,
            'email': email,
            'type': 'email_verification',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        save_verification_tokens(tokens)
        
        # Send verification email
        subject, html_content, text_content = create_verification_email(email, token, 'email_verification')
        email_sent = send_email(email, subject, html_content, text_content)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Verification email has been resent.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send verification email. Please try again.'
            })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user (no email verification required)"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Load users
        users = load_users()
        
        # Check if user exists
        if username not in users:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # No email verification check
        # Verify password
        if not verify_password(password, users[username]['password']):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Update last login
        users[username]['last_login'] = datetime.now().isoformat()
        save_users(users)
        
        # Log in the user
        session['user_id'] = username
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'username': username,
                'email': users[username].get('email', ''),
                'email_verified': True,
                'created_at': users[username]['created_at'],
                'last_login': users[username]['last_login']
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
        
        # Load user info
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
                'email_verified': users[user_id].get('email_verified', False),
                'created_at': users[user_id]['created_at'],
                'last_login': users[user_id]['last_login']
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/auth/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Validate new password strength
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        user_id = get_current_user()
        users = load_users()
        
        # Verify current password
        if not verify_password(current_password, users[user_id]['password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        users[user_id]['password'] = hash_password(new_password)
        save_users(users)
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def load_verification_tokens():
    """Load verification tokens from JSON file"""
    if os.path.exists(VERIFICATION_TOKENS_FILE):
        try:
            with open(VERIFICATION_TOKENS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_verification_tokens(tokens):
    """Save verification tokens to JSON file"""
    with open(VERIFICATION_TOKENS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)

def send_email(to_email, subject, html_content, text_content=None):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = to_email
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email sending error: {e}")
        return False

def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)

def create_verification_email(email, token, token_type='email_verification'):
    """Create email verification email"""
    if token_type == 'email_verification':
        subject = f"Verify your email - {EMAIL_CONFIG['app_name']}"
        verification_url = f"http://localhost:5000/api/auth/verify-email?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to {EMAIL_CONFIG['app_name']}!</h2>
            <p>Thank you for registering. Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}" style="background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Verify Email</a></p>
            <p>Or copy and paste this link in your browser:</p>
            <p>{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, you can safely ignore this email.</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to {EMAIL_CONFIG['app_name']}!
        
        Thank you for registering. Please verify your email address by visiting:
        {verification_url}
        
        This link will expire in 24 hours.
        If you didn't create an account, you can safely ignore this email.
        """
    
    elif token_type == 'password_reset':
        subject = f"Reset your password - {EMAIL_CONFIG['app_name']}"
        reset_url = f"http://localhost:5000/reset-password.html?token={token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password for {EMAIL_CONFIG['app_name']}.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}" style="background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">Reset Password</a></p>
            <p>Or copy and paste this link in your browser:</p>
            <p>{reset_url}</p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request a password reset, you can safely ignore this email.</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        You requested to reset your password for {EMAIL_CONFIG['app_name']}.
        Visit this link to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        If you didn't request a password reset, you can safely ignore this email.
        """
    
    return subject, html_content, text_content

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

if __name__ == '__main__':
    print("🚀 Starting Personal Daily Journal API...")
    print("📖 Open http://localhost:5000 in your browser")
    print("📝 API will be available at http://localhost:5000/api/journal")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Use environment variables for production deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port) 