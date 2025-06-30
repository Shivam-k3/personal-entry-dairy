from http.server import BaseHTTPRequestHandler
import json
import os
import hashlib
import re
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# File paths
USERS_FILE = 'users.json'

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

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

class AuthHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for authentication"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            path = self.path
            
            if path == '/api/auth/register':
                response = self.handle_register(data)
            elif path == '/api/auth/login':
                response = self.handle_login(data)
            elif path == '/api/auth/logout':
                response = self.handle_logout()
            else:
                response = {'error': 'Invalid endpoint'}, 404
                
        except json.JSONDecodeError:
            response = {'error': 'Invalid JSON'}, 400
        except Exception as e:
            response = {'error': f'Server error: {str(e)}'}, 500
        
        self.send_response(response[1])
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(response[0]).encode())
    
    def do_GET(self):
        """Handle GET requests for auth status"""
        if self.path == '/api/auth/status':
            response = self.handle_auth_status()
        else:
            response = {'error': 'Invalid endpoint'}, 404
        
        self.send_response(response[1])
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response[0]).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_register(self, data):
        """Handle user registration"""
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return {'error': 'Username, email, and password are required'}, 400
        
        # Validate inputs
        if not validate_username(username):
            return {'error': 'Username must be 3-20 characters and alphanumeric'}, 400
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return {'error': error_msg}, 400
        
        if not validate_email(email):
            return {'error': 'Invalid email format'}, 400
        
        # Load existing users
        users = load_users()
        
        # Check if username or email already exists
        if username in users:
            return {'error': 'Username already exists'}, 400
        
        for user_data in users.values():
            if user_data.get('email') == email:
                return {'error': 'Email already registered'}, 400
        
        # Create user
        users[username] = {
            'username': username,
            'email': email,
            'password': hash_password(password),
            'email_verified': True,  # Skip email verification for demo
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        save_users(users)
        
        return {
            'success': True,
            'message': 'Registration successful! You can now login.'
        }, 200
    
    def handle_login(self, data):
        """Handle user login"""
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return {'error': 'Username and password are required'}, 400
        
        users = load_users()
        
        if username not in users:
            return {'error': 'Invalid username or password'}, 401
        
        user = users[username]
        
        if not verify_password(password, user['password']):
            return {'error': 'Invalid username or password'}, 401
        
        # Update last login
        users[username]['last_login'] = datetime.now().isoformat()
        save_users(users)
        
        return {
            'success': True,
            'user': {
                'username': username,
                'email': user['email'],
                'email_verified': user.get('email_verified', True)
            }
        }, 200
    
    def handle_logout(self):
        """Handle user logout"""
        return {
            'success': True,
            'message': 'Logout successful'
        }, 200
    
    def handle_auth_status(self):
        """Handle auth status check"""
        return {
            'authenticated': False,
            'user': None
        }, 200

def handler(request, context):
    """Vercel serverless function handler"""
    return AuthHandler() 